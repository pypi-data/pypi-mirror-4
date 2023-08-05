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

import urllib

from django.conf import settings
from sections import (
    ErrorSummarySection,
    ExceptionsSection,
    TimeOutSection,
    TimeOutCountSection,
    StatementCountSection,
    TopDurationSection,
    HARD_TIMEOUT_EXCEPTIONS,
    SOFT_TIMEOUT_EXCEPTIONS,
)


class ErrorSummary:
    """Summary of Oops that happened in a given date [range]. A summary
    is composed by the stats and then the individual error sections.
    """
    #TODO matsubara: maybe stats could be another type of section?

    def __init__(self):
        self.exc_count = 0
        self.start = None
        self.end = None
        self.sections_by_id = {}
        self.sections = []
        self.addSection(
            ExceptionsSection('Exceptions'))

    @property
    def period(self):
      #XXX missing docstring and test
        period = self.end - self.start
        days = period.days + period.seconds / 86400.0
        return days


    def addSection(self, section, index=None):
        """Add a section to the summary and populate sections_by_id
        dictionary.

        If optional index parameter is given, the section will be inserted
        before that index, otherwise it'll be appended to the end of the list.
        The sections_by_id dictionary holds all sections by their section_id.
        """
        if index is not None:
            self.sections.insert(index, section)
        else:
            self.sections.append(section)
        self.sections_by_id[section.section_id] = section

    def addOopsToSection(self, oops, section_id='exceptions'):
        """Add an Oops to the given section."""
        self.sections_by_id.get(section_id).addOops(oops)

    def processOops(self, oops):
        self.exc_count += 1

        # add the date to oopsid to make it unique
        if self.start is None or self.start > oops.date:
            self.start = oops.date
        if self.end is None or self.end < oops.date:
            self.end = oops.date

    def renderTXT(self, fp):
        fp.write("=== Statistics ===\n\n")
        fp.write(" * Log starts: %s\n" % self.start)
        fp.write(" * Analyzed period: %.2f days\n" % self.period)
        fp.write(" * Total OOPSes: %d\n" % self.exc_count)
        # Do not print Average OOPS if we have less than a day worth of oops.
        if self.period > 1:
            fp.write(" * Average OOPSes per day: %.2f\n\n" %
                     (self.exc_count / self.period))
        else:
            fp.write("\n")
        for section in self.sections:
            section.renderHeadlineTXT(fp)
        fp.write("\n")
        for section in self.sections:
            section.renderTXT(fp)

    def renderHTML(self, fp):
        fp.write('<html>\n'
                 '<head>\n'
                 '<title>Oops Report Summary</title>\n'
                 '<link rel="stylesheet" type="text/css" href="%s/oops/static/oops.css" />\n'
                 '</head>\n'
                 '<body>\n'
                 '<h1>Oops Report Summary</h1>\n\n' % settings.ROOT_URL)

        fp.write('<ul id="period">\n')
        fp.write('<li>Log starts: %s</li>\n' % self.start)
        fp.write('<li>Analyzed period: %.2f days</li>\n' % self.period)
        fp.write('<li>Total exceptions: %d</li>\n' % self.exc_count)
        # Do not print Average OOPS if we have less than a day worth of oops.
        if self.period > 1:
            fp.write('<li>Average exceptions per day: %.2f</li>\n' %
                     (self.exc_count / self.period))
        fp.write('</ul>\n\n')
        fp.write('<ul id="stats">\n')
        for section in self.sections:
            section.renderHeadlineHTML(fp)
        fp.write('</ul>\n\n')

        for section in self.sections:
            fp.write('<a name="%s"></a>' % section.section_id)
            section.renderHTML(fp)

        fp.write('</body>\n')
        fp.write('</html>\n')


class WebAppErrorSummary(ErrorSummary):
    """Summarize web app error reports"""

    def __init__(self):
        ErrorSummary.__init__(self)
        #XXX this index idea is bullshit
        self.addSection(
            TimeOutCountSection("Time Out Counts by Page ID"), index=0)
        self.addSection(
            StatementCountSection("Statement Counts"), index=0)
        self.addSection(
            TopDurationSection("Durations"), index=0)
        self.addSection(TimeOutSection('Time Outs'))
        self.addSection(TimeOutSection('Soft Time Outs'))
        self.addSection(ErrorSummarySection('Informational Only Errors'))
        self.addSection(ErrorSummarySection('User Generated Errors'))
        self.addSection(ErrorSummarySection('Unauthorized Errors'))
        self.addSection(ErrorSummarySection('Pages Not Found'))

    def processOops(self, oops):
        ErrorSummary.processOops(self, oops)

        # First, for the two global sections, always add the oops
        self.addOopsToSection(oops, section_id='statement-counts')
        self.addOopsToSection(oops, section_id='durations')

        def is_non_ascii(url):
            """Return True if url contains non-ascii characters"""
            try:
                urllib.unquote(url).encode('ascii')
            except UnicodeError:
                return True
            else:
                return False

        if oops.exception_type in HARD_TIMEOUT_EXCEPTIONS:
            self.addOopsToSection(
                oops, section_id='time-out-counts-by-page-id')
            self.addOopsToSection(oops, section_id='time-outs')
        elif oops.exception_type in SOFT_TIMEOUT_EXCEPTIONS:
            self.addOopsToSection(
                oops, section_id='time-out-counts-by-page-id')
            self.addOopsToSection(oops, section_id='soft-time-outs')
        elif oops.exception_type in ['Unauthorized']:
            self.addOopsToSection(oops, section_id='unauthorized-errors')
        elif oops.exception_type in ['NotFound',
                                     'DeletedProxiedLibraryFileAlias',
                                     'GoneError']:
            self.addOopsToSection(oops, section_id='pages-not-found')
        elif oops.exception_type in ['UnexpectedFormData',
                                     'OffsiteFormPostError',
                                     'ProtocolErrorException',
                                     'InvalidBatchSizeError',
                                     'UnsupportedFeedFormat',
                                     'UntrustedReturnURL',
                                     'UserRequestOops']:
            self.addOopsToSection(oops, section_id='user-generated-errors')
        elif oops.informational:
            self.addOopsToSection(oops, section_id='informational-only-errors')
        elif oops.exception_type in ['UnicodeEncodeError', 'TypeError',
                                     'ProgrammingError'] and ('@@' in oops.url
                                        or is_non_ascii(oops.url)):
            self.addOopsToSection(oops, section_id='user-generated-errors')
        else:
            self.addOopsToSection(oops)


class CodeHostingWithRemoteSectionSummary(ErrorSummary):
    """Summarize errors reports including a section for remote errors."""

    def __init__(self):
        ErrorSummary.__init__(self)
        self.addSection(ErrorSummarySection('Remote Errors'))

    def processOops(self, oops):
        ErrorSummary.processOops(self, oops)
        if oops.exception_type in ["ConnectionError", "InvalidHttpResponse",
                                   "TimeoutError", "NotBranchError",
                                   "UnsupportedFormatError",
                                   "UnknownFormatError",
                                   "BranchReferenceForbidden",
                                   "BranchReferenceValueError",
                                   "BranchReferenceLoopError",
                                   "InvalidURIError"]:
            self.addOopsToSection(oops, section_id="remote-errors")
        else:
            self.addOopsToSection(oops)


class CheckwatchesErrorSummary(ErrorSummary):
    """Summarize checkwatches error reports"""

    def __init__(self):
        ErrorSummary.__init__(self)
        self.addSection(ErrorSummarySection('Remote Checkwatches Warnings'))

    def processOops(self, oops):
        ErrorSummary.processOops(self, oops)
        if oops.exception_type in ["BugTrackerConnectError",
                                   "BugWatchUpdateWarning",
                                   "UnknownRemoteStatusError", "InvalidBugId",
                                   "BugNotFound"]:
            self.addOopsToSection(
                oops, section_id='remote-checkwatches-warnings')
        else:
            self.addOopsToSection(oops)


class GenericErrorSummary(ErrorSummary):
    """An error summary with only the exception section."""

    def processOops(self, oops):
        ErrorSummary.processOops(self, oops)
        self.addOopsToSection(oops)
