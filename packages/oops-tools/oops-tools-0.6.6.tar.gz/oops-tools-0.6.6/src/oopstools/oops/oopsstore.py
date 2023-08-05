# Copyright 2005-2011 Canonical Ltd.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


__metaclass__ = type

import re
import os
import datetime
import itertools

from oopstools.oops.models import Oops, OopsReadError, oops_re


# the section of the OOPS ID before the instance identifier is the
# days since the epoch, which is defined as the start of 2006.
epoch = datetime.datetime(2006, 01, 01, 00, 00, 00)


class OopsNotFound(LookupError):
    pass


class OopsStore:
    """A collection of OOPS reports"""

    def __init__(self, oopsdir):
        """Create an OOPS store.

        The oopsdir parameter is the top directory in the directory tree
        containing oops reports. Each directory in the dir tree should
        contain subdirectories of the form YYYY-mm-dd, which in turn contain
        the OOPS reports.
        """
        self.oopsdirs = set()
        date_pat = re.compile('\d{4}-\d{2}-\d{2}')

        # This is an optimization to find the directories.
        # os.walk() was previously used here but it was taking too much time.
        def find_dirs(dirs):
            for dir in dirs:
                if not os.path.isdir(dir):
                    # XXX: untested
                    continue
                try:
                    # Filter out filenames. We only want directories.
                    subdirs = [d for d in os.listdir(dir) if os.path.isdir(
                        os.path.join(dir, d))]
                except OSError:
                    # Can't list dir, permission denied. Ignore it.
                    continue
                if not subdirs:
                    # dir is empty. Ignore it.
                    continue
                os.chdir(dir)
                # Sort subdirs so date directories, if any, will show up as
                # first.
                sorted_subdirs = sorted(subdirs)
                if date_pat.match(sorted_subdirs[0]):
                    self.oopsdirs.add(os.getcwd())
                else:
                    find_dirs(subdirs)
                os.chdir("..")

        # XXX matsubara: remove the if clause when refactoring this code
        # to use a single oops directory.
        if type(oopsdir) == str:
            oopsdir = [oopsdir,]
        # XXX matsubara: find_dirs changes directories to do its job and
        # before calling it, record the original directory the script is
        # in and after it finishes building
        # self.oopsdirs set, the script returns to the original place.
        original_working_dir = os.getcwd()
        find_dirs(oopsdir)
        os.chdir(original_working_dir)

    def find_oops(self, oopsid):
        """Get an OOPS report by oopsid."""
        date, oops = self.canonical_name(oopsid).split('/', 1)
        oops_prefix = oops_re.match(oops).group('oopsprefix')
        # now find the OOPS:
        for oopsdir in self.oopsdirs:
            datedir = os.path.join(oopsdir, date)
            if not os.path.isdir(datedir):
                continue
            for filename in sorted(os.listdir(datedir)):
                original_filename = filename
                # Normalize filename
                filename = filename.upper()
                if (oops_prefix in filename and
                    (filename.endswith('.' + oops) or
                    filename.endswith('.' + oops + '.BZ2') or
                    filename.endswith('.' + oops + '.GZ') or
                    # U1/ISD oops reports use different filename scheme.
                    filename.endswith(oops + '.OOPS') or
                    filename.endswith(oops + '.OOPS.BZ2'))):
                    return Oops.from_pathname(
                        os.path.join(datedir, original_filename))
        else:
            raise OopsNotFound("Could not find OOPS")

    def canonical_name(self, name):
        """Canonicalise an OOPS report name."""
        match = oops_re.match(name.upper())
        if not match:
            raise OopsNotFound("Invalid OOPS name")

        now = datetime.datetime.utcnow()

        date = match.group('date')
        dse = match.group('dse')
        oops = match.group('oopsprefix') + match.group('id')
        if date:
            pass # got enough data
        elif dse:
            # dse is the number of days since the epoch
            day = epoch + datetime.timedelta(days=int(dse) - 1)
            date = '%04d-%02d-%02d' % (day.year, day.month, day.day)
        else:
            # Assume the OOPS is from today
            date = '%04d-%02d-%02d' % (now.year, now.month, now.day)

        return '%s/%s' % (date, oops)

    def _get_oops_prefix(self, filename):
        """Return oops prefix for a given filename."""
        if filename.upper().endswith((".OOPS", ".OOPS.BZ2")):
            # Got a U1/ISD oops report.
            oops_prefix = filename.split(".", 1)[0]
            oops_prefix = re.split("\d+", oops_prefix)[2]
        else:
            #XXX: matsubara 2009-11-06 bug=353945 There's a disparity
            # between the OOPS filename and the OOPS id, that's why
            # there're two different regex to identify those.
            oops_prefix = filename.split(".")[1]
            oops_prefix = re.sub("\d+$", "",  oops_prefix)
        # Normalize oops prefix
        return oops_prefix.upper()

    def _search(self, startdate, enddate, prefixes=None):
        """Yield each OOPS report between the given two dates."""
        date = startdate
        while date <= enddate:
            datestr = date.strftime('%Y-%m-%d')
            for oopsdir in self.oopsdirs:
                datedir = os.path.join(oopsdir, datestr)
                if not os.path.isdir(datedir):
                    continue
                for filename in sorted(os.listdir(datedir)):
                    oops_prefix = self._get_oops_prefix(filename)
                    if prefixes:
                        if oops_prefix not in prefixes:
                            # Didn't match my prefix, get outta here
                            continue
                    try:
                        yield Oops.from_pathname(
                            os.path.join(datedir, filename))
                    except OopsReadError:
                        # ignore non-OOPS reports
                        pass
            date += datetime.timedelta(days=1)

    def search(self, startdatetime, enddatetime, prefixes=None):
        """Return a generator with OOPSes between the given two datetimes."""
        oops_results = self._search(startdatetime, enddatetime, prefixes)
        if not startdatetime.time() and not enddatetime.time():
            # Faster to just return the generator from _search() when there's
            # only date and no time.
            return oops_results
        else:
            return itertools.ifilter(
                lambda oops: startdatetime <= oops.date <= enddatetime,
                oops_results)
