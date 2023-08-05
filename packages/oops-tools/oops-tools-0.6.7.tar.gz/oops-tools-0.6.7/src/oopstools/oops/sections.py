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



import oopsgroup

from django.conf import settings

HARD_TIMEOUT_EXCEPTIONS = ['RequestExpired',
                           'RequestStatementTimedOut',
                           'TimeoutError',
                           'LaunchpadTimeoutError']
SOFT_TIMEOUT_EXCEPTIONS = ['SoftRequestTimeout']
TIMEOUT_EXCEPTIONS = HARD_TIMEOUT_EXCEPTIONS + SOFT_TIMEOUT_EXCEPTIONS


def get_safe_pageid(oops):
    """Always return a useful Page ID or, if Unknown, the URL."""
    if oops.pageid == "Unknown":
        return oops.url
    return oops.pageid


class ErrorSummarySection:
    """A section in the error summary."""

    max_count = 15

    def __init__(self, title):
        self.oops_groups = {}
        self.title = title
        self.section_id = title.lower().replace(" ", "-")

    def addOops(self, oops):
        etype = oops.exception_type
        evalue = oops.normalized_exception_value

        oops_group = self.oops_groups.setdefault((etype, evalue),
                                    oopsgroup.OopsGroup(etype, evalue))
        oops_group.addOops(oops)

    def renderHeadlineTXT(self, fp):
        """Render this section stats header in plain text."""
        fp.write(' * %d %s\n' % (
            self.errorCount(), self.title))

    def renderHeadlineHTML(self, fp):
        """Render this section stats header in HTML."""
        fp.write('<li><a href="#%s">%d %s</a></li>\n' %
            (self.section_id, self.errorCount(), self.title))

    def errorCount(self):
      #XXX missing test and docstring and better name
       return sum(
           group.count for group in self.oops_groups.itervalues())

    def renderTXT(self, fp):
        """Render this section in plain text."""
        groups = sorted(self.oops_groups.itervalues(),
                        key=lambda group: (group.count, group.etype,
                                           group.evalue),
                        reverse=True)

        total = len(groups)
        if self.max_count >= 0 and total > self.max_count:
            fp.write('=== Top %d %s (total of %s unique items) ===\n\n' % (
                self.max_count, self.title, total))
            groups = groups[:self.max_count]
        else:
            fp.write('=== All %s ===\n\n' % self.title)

        for group in groups:
            group.renderTXT(fp)
        fp.write('\n')

    def renderHTML(self, fp):
        """Render this section in HTML."""
        fp.write('<div id="%s">' % self.section_id)
        fp.write('<h2>All %s</h2>\n' % self.title)
        groups = sorted(self.oops_groups.itervalues(),
                        key=lambda group: (group.count, group.etype,
                                           group.evalue),
                        reverse=True)
        for group in groups:
            group.renderHTML(fp)
        fp.write('</div>')


class ExceptionsSection(ErrorSummarySection):
    """A section in the error summary."""
    max_count = 50


class TimeOutSection(ErrorSummarySection):
    """Timeout section in the error summary."""

    def addOops(self, oops):
        etype = oops.most_expensive_statement
        evalue = ''
        oops_group = self.oops_groups.setdefault((etype, evalue),
                                    oopsgroup.OopsGroup(etype, evalue))
        oops_group.addOops(oops)


class TimeOutCountSection(ErrorSummarySection):
    """The timeout counts by page id section."""
    max_count = 10

    def __init__(self, title):
        ErrorSummarySection.__init__(self, title)
        self.soft_timeouts = {}
        self.hard_timeouts = {}
        self.cached_timeouts_by_pageid = []

    def addOops(self, oops):
        etype = oops.exception_type
        assert etype in TIMEOUT_EXCEPTIONS
        pageid = get_safe_pageid(oops)
        if etype in SOFT_TIMEOUT_EXCEPTIONS:
            timeouts = self.soft_timeouts
        elif etype in HARD_TIMEOUT_EXCEPTIONS:
            timeouts = self.hard_timeouts
        else:
            raise AssertionError(
                "%s is %s, not a timeout" % (oops.oopsid, etype))
        timeouts.setdefault(pageid, 0)
        timeouts[pageid] += 1

    def renderHeadlineTXT(self, fp):
        return

    def renderHeadlineHTML(self, fp):
        fp.write(
            '<li><a href="#%s">%s</a></li>\n' % (self.section_id, self.title))

    def renderTXT(self, fp):
        fp.write('=== Top %d %s ===\n\n' % (self.max_count, self.title))
        fp.write('     Hard / Soft  Page ID\n')
        for ht, st, pageid in self._calculateTimeOutCounts():
            fp.write('%9s / %4s  %s\n' % (ht, st, pageid))
        fp.write('\n\n')

    def renderHTML(self, fp):
        fp.write('<div id="%s">' % self.section_id)
        fp.write('<h2>%s</h2>\n' % self.title)
        fp.write('<table class="top-value-table">\n')
        fp.write('<tr>\n')
        fp.write('<th>Hard</th>\n')
        fp.write('<th>Soft</th>\n')
        fp.write('<th>Page ID</th>\n')
        fp.write('</tr>\n')
        for ht, st, pageid in self._calculateTimeOutCounts():
            fp.write('<tr>\n')
            fp.write('<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n' %
                (ht, st, pageid))
            fp.write('</tr>\n')
        fp.write('</table>')
        fp.write('</div>')

    def _calculateTimeOutCounts(self):
        if self.cached_timeouts_by_pageid:
            return self.cached_timeouts_by_pageid[:self.max_count]

        # First, collect all the pageids that presented timeouts.
        pageid_set = set(self.soft_timeouts.keys())
        pageid_set = pageid_set.union(self.hard_timeouts.keys())
        # Then pick out the counts and display the section
        for pageid in pageid_set:
            st = self.soft_timeouts.get(pageid, 0)
            ht = self.hard_timeouts.get(pageid, 0)
            self.cached_timeouts_by_pageid.append((ht, st, pageid))
        self.cached_timeouts_by_pageid.sort(reverse=True)
        return self.cached_timeouts_by_pageid[:self.max_count]


class TopValueSection(ErrorSummarySection):
    """A base section for displaying top N sets of OOPSes."""
    max_count = 10

    def __init__(self, title):
        ErrorSummarySection.__init__(self, title)
        self.pageids = {}

    def addOops(self, oops):
        pageid = get_safe_pageid(oops)
        value = self.getValue(oops)
        if (self.pageids.has_key(pageid) and
            value <= self.pageids[pageid][0]):
                return
        self.pageids[pageid] = (value, oops.oopsid, pageid)

    def renderHeadlineTXT(self, fp):
        return

    def renderHeadlineHTML(self, fp):
        fp.write(
            '<li><a href="#%s">%s</a></li>\n' % (self.section_id, self.title))

    def formatValues(self, value, oopsid, pageid):
        formatted_value = self.formatValue(value)
        return '%s  %-14s  %s\n' % (formatted_value, oopsid, pageid)

    def renderHTML(self, fp):
        fp.write('<div id="%s">' % self.section_id)
        fp.write('<h2>%s</h2>\n' % self.title)
        fp.write('<table class="top-value-table">\n')
        fp.write('<tr>\n')
        fp.write('<th>%s</th>\n' % self.value_name)
        fp.write('<th>Oops ID</th>\n')
        fp.write('<th>Page</th>\n')
        fp.write('</tr>\n')
        for value, oopsid, pageid in self.getValues():
            fp.write('<tr>\n')
            fp.write('<td>%s</td>\n<td><a href="%s/oops/?oopsid=%s">%s</a></td>'
                     '\n<td>%s</td>\n' % (
                        self.formatValue(value), settings.ROOT_URL,
                        oopsid, oopsid, pageid))
            fp.write('</tr>\n')
        fp.write('</table>')
        fp.write('</div>')

    def renderTXT(self, fp):
        fp.write('=== Top %d %s ===\n\n' % (self.max_count, self.title))
        for duration, oopsid, pageid in self.getValues():
            fp.write(self.formatValues(duration, oopsid, pageid))
        fp.write('\n\n')

    def getValues(self):
        """Yield all values in this class sorted by highest value."""
        for value, oopsid, pageid in sorted(self.pageids.values(),
                                            reverse=True)[:self.max_count]:
            yield (value, oopsid, pageid)

    def getValue(self, oops):
        """Return the value for which this OOPS will be evaluted.

        This class attempts to collect the OOPSes with the highest
        values; this method allows you to specify which attribute of
        the OOPS you are considering.
        """
        raise NotImplementedError

    def formatValue(self, value):
        """Format the value obtained for rendering.

        In normal situations the value should be formatted with 9
        spaces.
        """
        raise NotImplementedError


class StatementCountSection(TopValueSection):
    """The top statement counts section."""
    value_name = "Count"

    def getValue(self, oops):
        return oops.statements_count

    def formatValue(self, value):
        return '%9d' % value


class TopDurationSection(TopValueSection):
    """The top page IDs by duration."""
    value_name = "Duration"

    def getValue(self, oops):
        return oops.duration

    def formatValue(self, value):
        return '%9.2fs' % value

