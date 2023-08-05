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

# Analyse error reports and return a list of most frequent errors

__metaclass__ = type

import sys
import optparse
import StringIO

from oopstools.oops.helpers import parsedate, load_prefixes
from oopstools.oops.models import (
    Prefix,
    Report,
    )
from oopstools.oops import dbsummaries


def main(argv=None):

    usage = "%prog [options] oops-reports-directory"
    description = "This script summarises Launchpad OOPS reports"

    if argv is None:
        argv=sys.argv

    epilog = "The prefix option can be used multiple times."

    parser = optparse.OptionParser(
        description=description, epilog=epilog, usage=usage)

    parser.add_option('--verbose', action="store_true",
                      help="Enable verbose output.",
                      dest='verbose', default=False)
    parser.add_option('--from', metavar='DATE', action='store',
                      help=("The start date (REQUIRED), as YYYY-MM-DD "
                      "[HH:MM:SS]. Time is optional."),
                      type='string', dest='startdate', default=None)
    parser.add_option('--to', metavar='DATE', action='store',
                      help=("The end date, as YYYY-MM-DD [HH:MM:SS]. If "
                      "omitted, defaults to one day after the start date."),
                      type='string', dest='enddate', default=None)
    parser.add_option('--text', metavar='FILE', action='store',
                      help='filename to store text version of report',
                      type='string', dest='text', default=None)
    parser.add_option('--html', metavar='FILE', action='store',
                      help='filename to store HTML version of report',
                      type='string', dest='html', default=None)

    oops_prefixes = list(Prefix.objects.all().values_list('value', flat=True))
    parser.add_option('-p', '--prefix', metavar='PREFIX', action='append',
                      type='choice', choices=oops_prefixes, dest='prefixes',
                      default=None)
    parser.add_option('-r', '--report', metavar='REPORT', action='append',
                      dest='report', default=None,
                      help='Use all prefixes from this report.')

    options, args = parser.parse_args(argv[1:])

    ## Process start and end dates
    # Means that no startdate was given, but it's required
    if options.startdate is None:
        parser.error('Missing start date.\n')
        sys.exit(1)

    try:
        startdate = parsedate(options.startdate)
    except ValueError:
        parser.error('Wrong date format. Use: YYYY-MM-DD [HH:MM:SS]\n')
        sys.exit(1)

    # if enddate is not given, set it to startdate, so we get a single
    # day's data.
    if options.enddate is None:
        enddate = startdate
    else:
        try:
            enddate = parsedate(options.enddate)
        except ValueError:
            parser.error('Wrong date format. Use: YYYY-MM-DD [HH:MM:SS]\n')
            sys.exit(1)

    if args:
        parser.error('No arguments are accepted.\n')
        sys.exit(1)

    # parse error reports
    if options.report:
        if not options.prefixes:
            options.prefixes = []
        for report in options.report:
            prefixes = load_prefixes(report)
            options.prefixes.extend(prefixes)

    # Same default
    summary = dbsummaries.GenericErrorSummary
    if options.prefixes:
        # But maybe all the prefixes match a canned report, if so we should use
        # that.
        prefixes_arg = set(options.prefixes)
        summary_map = dict(Report.SUMMARY_CHOICES)
        for report in Report.objects.all():
            report_prefixes = set(
                prefix.value for prefix in report.prefixes.all())
            if prefixes_arg.issubset(report_prefixes):
                summary_class_name = summary_map[report.summary]
                summary = getattr(dbsummaries, summary_class_name)

    summary = summary(startdate, enddate, options.prefixes)

    if not summary.count:
        sys.stderr.write("No oopses found on the given date interval.\n")
        sys.exit(1)

    if options.html:
        fp = open(options.html, 'wb')
        summary.renderHTML(fp)
        fp.close()
    if options.text:
        fp = open(options.text, 'wb')
        summary.renderTXT(fp)
        fp.close()
    if options.html is None and options.text is None:
        summary.renderTXT(sys.stdout)


def test_main(args):
    """Convenience function for tests."""
    original_out, original_err = sys.stdout, sys.stderr
    sys.stdout = StringIO.StringIO()
    sys.stderr = StringIO.StringIO()
    # Catch SystemExit here so we can test the error messages.
    try:
        main(args)
    except SystemExit:
        pass
    res = (sys.stdout.getvalue(), sys.stderr.getvalue())
    sys.stdout, sys.stderr = original_out, original_err
    return res
