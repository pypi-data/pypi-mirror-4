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

import datetime
import os
import re
import stat

from django.conf import settings
from django.db import transaction, IntegrityError

from oopstools.oops.helpers import today
from oopstools.oops.log import get_logger
from oopstools.oops.models import Oops, OopsReadError, DBOopsRootDirectory


logger = get_logger('OopsLoader', 'update_db.log')


# YYYY-MM-DD pattern to match OOPS subdirectories.
date_pat = re.compile('^\d{4}-\d{2}-\d{2}$')


def is_dir(full_path, subdir):
    """Return true if full_path/subdir is a real on-disk directory."""
    try:
        is_dir = stat.S_ISDIR(
            os.lstat(os.path.join(full_path, subdir)).st_mode)
    except OSError:
        is_dir = False
    return is_dir


def _find_dirs(dirs, root=''):
    """Find OOPS directories in the OOPS dir tree."""
    matching_dirs = []
    # This is an optimization to find the directories.
    # os.walk() was previously used here but it was taking too much time.
    for current in dirs:
        full_path = os.path.join(root, current)
        if not is_dir(full_path, ''):
            continue
        try:
            subdirs = [subdir for subdir in os.listdir(full_path)
                       if is_dir(full_path, subdir)]
        except OSError:
            continue

        date_dir_found = False
        non_date_dirs = []
        for subdir in subdirs:
            if date_pat.match(subdir):
                date_dir_found = True
            else:
                non_date_dirs.append(subdir)

        if date_dir_found:
            matching_dirs.append(full_path)
        matching_dirs.extend(_find_dirs(non_date_dirs, full_path))

    return matching_dirs


def oops_dir_finder(oopsdir):
    """Search the filesystem for OOPS directories.

    The oopsdir parameter is the top directory in the directory tree
    containing oops reports. Each directory in the dir tree should
    contain subdirectories of the form YYYY-mm-dd, which in turn contain
    the OOPS reports.
    """
    # XXX matsubara: remove the if clause when refactoring this code
    # to use a single oops directory.
    if type(oopsdir) == str:
        oopsdir = [oopsdir,]

    # Walk through all subdirectories containing OOPSes and ensure there
    # is a matching database structure for them.
    for root_dir in _find_dirs(oopsdir):
        try:
            DBOopsRootDirectory.objects.get(root_dir__exact=root_dir)
        except DBOopsRootDirectory.DoesNotExist:
            oopsrootdir = DBOopsRootDirectory(
                root_dir=root_dir, last_date=None, last_oops=None)
            oopsrootdir.save()


class OopsLoader:
    """Load a collection of OOPS reports on the filesystem into the DB.

    This class is similar to OopsStore with the difference that it keeps the
    last added OOPS for each oops dir stored.
    """

    def __init__(self):
        """Create an OOPS loader."""
        self.oopsdirs = DBOopsRootDirectory.objects.all().order_by('root_dir')
        if not self.oopsdirs:
            oops_dir_finder(settings.OOPSDIR)
            self.oopsdirs = DBOopsRootDirectory.objects.all().order_by(
                'root_dir')

    def find_oopses(self, start_date):
        """Find OOPS reports in the filesystem and load them into the DB."""
        for entry in self.oopsdirs:
            if entry.last_date is not None and entry.last_date >= start_date:
                # Do not scan days we have previously completed.
                date = entry.last_date
            else:
                date = start_date
            while date <= today():
                datestr = date.strftime("%Y-%m-%d")
                datedir = os.path.join(entry.root_dir, datestr)
                if os.path.isdir(datedir):
                    oops_files = set(os.listdir(datedir))
                    # Query for all oopses on
                    # Search for datedir/% (so that we don't match other dirs
                    # that are a string suffix).
                    if not datedir.endswith('/'):
                        prefix = datedir + '/'
                    else:
                        prefix = datedir
                    # Allow for machines incorrectly setting datestamps (e.g.
                    # tz issues + daylight savings) on either side of the day
                    # we want.
                    before_date = date - datetime.timedelta(days=1)
                    after_date = date + datetime.timedelta(days=2)
                    query = Oops.objects.filter(
                        date__range=(before_date,after_date),
                        pathname__startswith=prefix).values_list(
                        'pathname', flat=True)
                    oops_reports = set(
                        os.path.basename(pathname) for pathname in query)
                    new_files = oops_files - oops_reports
                    for filename in sorted(new_files):
                        oops = self._load_oops(datedir, filename)
                        if oops is not None:
                            yield oops
                        # We update the last_date only when oops 
                        # has the date different to what we already have
                        # This speeds up the loading process
                        if entry.last_date != date:
                            entry.last_date = date
                            entry.save()
                date += datetime.timedelta(days=1)

    def _load_oops(self, datedir, filename):
        """Load an OOPS report into the database."""
        try:
            return Oops.from_pathname(
                os.path.join(datedir, filename))
        except OopsReadError:
            # ignore non-OOPS reports
            pass
        except IntegrityError, e:
            error_message = (
                'duplicate key value violates unique'
                ' constraint "oops_oops_pathname_key"')
            if str(e) == error_message:
                # This can happen if an oops view creates an
                # oops at the same time, causing a race
                # condition.
                logger.error(
                    "OOPS %s/%s already in the DB.", datedir, filename)
                transaction.rollback() # Continue to next one.
            else:
                logger.error(
                    "%s raised with datedir: %s filename: %s ",
                    e, datedir, filename)
                raise
        except Exception, e:
            logger.error(
                "%s raised with datedir: %s filename: %s ",
                e, datedir, filename)
            raise
