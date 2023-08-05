# Copyright 2007-2011 Canonical Ltd.  All rights reserved.
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

"""
Infamous helper functions.

BeautifulSoup-related helpers ripped off
canonical.launchpad.ftests.test_system_documentation.
"""

__metaclass__ = type

import os
import re
import time
from datetime import date, datetime

from django.conf import settings

from BeautifulSoup import (BeautifulSoup, Comment, Declaration,
    NavigableString, PageElement, ProcessingInstruction, Tag)


IGNORED_ELEMENTS = [Comment, Declaration, ProcessingInstruction]
ELEMENTS_INTRODUCING_NEWLINE = [
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'pre', 'dl',
    'div', 'noscript', 'blockquote', 'form', 'hr', 'table', 'fieldset',
    'address', 'li', 'dt', 'dd', 'th', 'td', 'caption', 'br']


NEWLINES_RE = re.compile(u'\n+')
LEADING_AND_TRAILING_SPACES_RE = (
    re.compile(u'(^[ \t]+)|([ \t]$)', re.MULTILINE))
TABS_AND_SPACES_RE = re.compile(u'[ \t]+')
NBSP_RE = re.compile(u'&nbsp;|&#160;')


def extract_text(content):
    """Return the text stripped of all tags.

    All runs of tabs and spaces are replaced by a single space and runs of
    newlines are replaced by a single newline. Leading and trailing white
    spaces is stripped.
    """
    if not isinstance(content, PageElement):
        soup = BeautifulSoup(content)
    else:
        soup = content

    result = []
    nodes = list(soup)
    while nodes:
        node = nodes.pop(0)
        if type(node) in IGNORED_ELEMENTS:
            continue
        elif isinstance(node, NavigableString):
            result.append(unicode(node))
        else:
            if isinstance(node, Tag):
                if node.name.lower() in ELEMENTS_INTRODUCING_NEWLINE:
                    result.append(u'\n')
            # Process this node's children next.
            nodes[0:0] = list(node)

    text = u''.join(result)
    text = NBSP_RE.sub(' ', text)
    text = TABS_AND_SPACES_RE.sub(' ', text)
    text = LEADING_AND_TRAILING_SPACES_RE.sub('', text)
    text = NEWLINES_RE.sub('\n', text)

    # Remove possible newlines at beginning and end.
    return text.strip()


def replace_variables(s):
    """Replace string and int variables on SQL statements.

    Also collapses sequences of $INTs to $INT ... $INT.

    See helpers.txt for tests and use cases.
    """
    s = re.sub(r"'[^']*'", '$STRING', s)
    s = re.sub(r'u"(?:\"|[^"])*"', '$STRING', s)
    s = re.sub(r'\b\d+', '$INT', s)
    s = re.sub(r'\$INT,(\s{0,1}\$INT,)+\s{0,1}\$INT', '$INT ... $INT', s)
    return s


def parsedate(date_string):
    """Return a naive date time object for the given string.

    This function ignores subsecond accuracy and the timezone. 
    May be used to parse a ISO 8601 date string.

    >>> ds = '2009-01-02'
    >>> parsedate(ds)
    datetime(2009, 1, 2, 0, 0)

    >>> ds = '2009-01-02 03:04:05'
    >>> parsedate(ds)
    datetime(2009, 1, 2, 3, 4, 5)

    >>> ds = '2009-01-02T03:04:05'
    >>> parsedate(ds)
    datetime(2009, 1, 2, 3, 4, 5)
    """
    ds = date_string[:19].replace("T", " ")
    try:
        year, month, day, hour, minute, second = time.strptime(
            ds, '%Y-%m-%d')[:6]
    except ValueError:
        # oops, wrong time format
        year, month, day, hour, minute, second = time.strptime(
            ds, '%Y-%m-%d %H:%M:%S')[:6]
    return datetime(year, month, day, hour, minute, second)


def generate_summary(prefixes, from_date, to_date=None, html_filename=None,
        extra_options=()):
    """Generate a summary with the given prefix and dates."""
    script_cmd = '%s/analyse_error_reports' % settings.BIN_DIR

    args = [script_cmd,]
    for prefix in prefixes:
        args.append("-p%s" % prefix)
    for d in (from_date, to_date):
        if isinstance(d, datetime):
            date_formatter = "%Y-%m-%d %H:%M:%S"
        elif isinstance(d, date):
            date_formatter = "%Y-%m-%d"
        else:
            continue
    args.append("--from=%s" % datetime.strftime(from_date, date_formatter))
    if to_date:
        args.append("--to=%s" % datetime.strftime(to_date, date_formatter))
    if html_filename:
        args.append("--html=%s" % html_filename)
    for option in extra_options:
        args.append(option)

    from oopstools.scripts.analyse_error_reports import test_main
    stdout, stderr = test_main(args)
    return stdout or stderr


def get_section_contents(title, text):
    """Get section contents on textual OOPS summary."""
    pattern = "=== %s ===" % title
    pos = text.find(pattern)
    if pos < 0:
        return "Pattern: '%s' not found in %s" % (pattern, text)
    return text[pos+len(pattern):].split("===")[0].strip()


def reset_database():
    """Delete all objects from Oops, DBOopsRootDirectory and Infestation."""
    from oopstools.oops.models import DBOopsRootDirectory, Infestation, Oops
    Oops.objects.all().delete()
    DBOopsRootDirectory.objects.all().delete()
    Infestation.objects.all().delete()
    assert Oops.objects.all().count() == 0
    assert DBOopsRootDirectory.objects.all().count() == 0
    assert Infestation.objects.all().count() == 0
    return "Oops, DBOopsRootDirectory and Infestation deleted."


def load_database(start_date, end_date=None, verbose=False):
    """Load sample data OOPS into the database."""
    from oopstools.oops.dboopsloader import OopsLoader
    loader = OopsLoader()
    if end_date:
        global _today
        _today = end_date
    found_oopses = list(loader.find_oopses(start_date))
    if verbose:
        count = 0
        for oops in found_oopses:
            count += 1
            print "Loaded %s" % oops.oopsid
        return "Loaded %d OOPSes into the database: %s" % (
            count, settings.DATABASE_NAME)
    return "Oopses loaded into the database."


def create_fake_oops(date):
    """Return the contents of a fake OOPS report based on a real one."""
    content = open(os.path.join(
        settings.OOPSDIR[0], 'dir1', '2007-11-20', '45084.S6')).read()
    from oopstools.oops.oopsstore import epoch
    # dse is the day since epoch. epoch is inclusive.
    dse = (date - epoch.date()).days + 1
    content = content.replace(
        'Oops-Id: OOPS-689S6', 'Oops-Id: OOPS-%sX1' % dse)
    return content.replace('Date: 2007-11-20T12:31:24.628042+00:00',
        'Date: %sT18:59:10.563701+00:00' % date.strftime("%Y-%m-%d"))


_cached_launchpadlib = None

def get_launchpadlib():
    """Return a launchpadlib instance from the cache.

    This function makes it easy to populate the cache with a fake
    launchpadlib instance to be used in tests or to run the code against
    the staging or lpnet API.
    """
    global _cached_launchpadlib
    if _cached_launchpadlib is None:
        from launchpadlib.launchpad import Launchpad
        _cached_launchpadlib = Launchpad.login_with('oops-tools', 'edge')
    return _cached_launchpadlib


_today = None

def today():
    """Return a date time object from the cache.

    This function makes it easy for test to use a cached date rather than the
    real date.
    """
    if _today is not None:
        return _today
    return date.today()


def load_prefixes(report_name):
    """Return a list of Prefix objects grouped by Report."""
    from oopstools.oops.models import Report 
    report = Report.objects.get(name=report_name)
    return [prefix.value for prefix in report.prefixes.all()]
