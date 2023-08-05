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

import cgi
import datetime

from zope.cachedescriptors.property import Lazy
from django.conf import settings
from django.db import connection
from django.db.models import Count, Max

from oopstools.oops.models import (
    Oops, Infestation, TIMEOUT_EXCEPTIONS)
from oopstools.oops.templatetags.oops_extras import get_absolute_url

__metaclass__ = type

TRACKED_HTTP_METHODS = ('GET', 'POST')

#############################################################################
# Groups

def _format_http_method_count(data):
    tmp = []
    for method in TRACKED_HTTP_METHODS + ('Other',):
        count = data.get(method)
        if count:
            tmp.append("%s: %s" % (method, count))
    return ' '.join(tmp)

def _escape(value):
    if value is not None:
        if not isinstance(value, unicode):
            # If a random byte string gets here, ensure it's ascii. Latin-1 is
            # used to decode so the escaped form matches the original bytes.
            value = value.decode("latin1").encode("ascii", "backslashreplace")
        else:
            value = value.encode("utf-8")
        value = cgi.escape(value)
    return value

# Add GroupConcat to aggregates.
from django.db.models.aggregates import Aggregate
from django.db.models.sql import aggregates
from django.db.models import DecimalField

class GroupConcat(aggregates.Aggregate):
    sql_function = 'GROUP_CONCAT'
    def __init__(self, col, source=None, **extra):
        # stolen from
        # http://www.mail-archive.com/django-users@googlegroups.com/msg74611.html
        aggregates.Aggregate.__init__(self, col, source=DecimalField(), **extra)
aggregates.GroupConcat = GroupConcat


class GroupConcat(Aggregate):
    name = 'GroupConcat'
# end GroupConcat

class SumBool(aggregates.Aggregate):
    sql_function = 'SUM'
    sql_template = (
        "%(function)s(CASE %(field)s WHEN True THEN 1 ELSE 0 END)")
    def __init__(self, col, source=None, **extra):
        aggregates.Aggregate.__init__(self, col, source=source, **extra)
aggregates.SumBool = SumBool

class SumBool(Aggregate):
    name = 'SumBool'


class AbstractGroup:

    max_urls = 5
    max_url_errors = 10

    # Set these in concrete __init__.
    etype = evalue = bug = errors = None

    def __init__(self, count, bot_count, local_referrer_count, url_count):
        self.count = count
        self.bot_count = int(bot_count)
        self.local_referrer_count = int(local_referrer_count)
        self.url_count = url_count

    def formatted_http_method_count(self):
        return _format_http_method_count(self.http_method_count)

    @Lazy
    def top_local_referrer(self):
        if self.local_referrer_count:
            local_referrers = (
                self.errors.filter(
                    is_local_referrer__exact=True).values(
                    'referrer').annotate(
                    count=Count('oopsid')).order_by(
                    'count', 'referrer').reverse())
            #XXX matsubara: hack?
            if local_referrers:
                return local_referrers[0]['referrer']
            else:
                return None
        # else: return None

    @Lazy
    def escaped_top_local_referrer(self):
        return _escape(self.top_local_referrer)

    @Lazy
    def top_urls(self):
        # This uses GroupConcat, a custom function supported natively by
        # sqlite and mysql, but one that would need emulation in postgres.
        # This is an optimization that lets us make one query instead of
        # many.
        res = (
            self.errors.values(
                'url', 'pageid').annotate(
                count=Count('oopsid'), errors=GroupConcat('oopsid')).order_by(
                '-count', 'url'))[:self.max_urls]
        for data in res:
            if data['url'].startswith(data['pageid']):
                data['pageid'] = 'Unknown'
            if data['pageid'] == '':
                data['pageid'] = 'Unknown'
            data['pageid'] = _escape(data['pageid'])
            data['escaped_url'] = _escape(data['url'])
            data['errors'] = data['errors'].split(',')
            data['errors'].sort()
            data['url'] = data['url'].encode('utf8')
        return res

    @Lazy
    def http_method_count(self):
        method_data = (
            self.errors.values(
                'http_method').annotate(
                count=Count('oopsid')))
        res = {}
        for d in method_data:
            if d['http_method'] in TRACKED_HTTP_METHODS:
                res[d['http_method']] = d['count']
            else:
                res['Other'] = res.get('Other', 0) + d['count']
        return res

    def renderTXT(self, fp):
        """Render this group in plain text."""
        fp.write('%4d %s: %s\n' % (
            self.count, self.etype.encode('utf8'), self.evalue.encode('utf8')))
        if self.bug:
            fp.write('    Bug: https://launchpad.net/bugs/%s\n' % self.bug)
        http_methods = self.formatted_http_method_count()
        fp.write('    %s Robots: %d  Local: %d'
                 % (http_methods, self.bot_count, self.local_referrer_count))
        if self.etype == 'NotFound' and self.local_referrer_count:
            fp.write(' Most Common Referrer: %s'
                % (self.top_local_referrer))
        fp.write('\n')
        max_urls = 3
        assert max_urls <= self.max_urls
        max_url_errors = 5
        for data in self.top_urls[:max_urls]:
            fp.write('    %(count)4d %(url)s (%(pageid)s)\n' % data)
            fp.write('        %s\n' %
                     ', '.join(data['errors'][:max_url_errors]))
        if self.url_count > max_urls:
            fp.write('    [%s other URLs]\n'
                     % (self.url_count - max_urls))
        fp.write('\n')

    def renderHTML(self, fp):
        """Render this group in HTML."""
        fp.write('<div class="exc">%d <b>%s</b>: %s</div>\n'
                 % (self.count, _escape(self.etype), _escape(self.evalue)))
        if self.bug:
            bug_link = "https://launchpad.net/bugs/%s" % self.bug
            fp.write('Bug: <a href="%s">%s</a>\n' % (bug_link, self.bug))
        http_methods = self.formatted_http_method_count()
        fp.write('<div class="pct">%s  Robots: %d  Local: %d'
                 % (http_methods, self.bot_count, self.local_referrer_count))
        if self.etype == 'NotFound' and self.local_referrer_count:
            referrer = self.escaped_top_local_referrer
            fp.write('  Most Common Referrer: <a href="%s">%s</a>'
                     % (referrer, referrer))
        fp.write('</div>\n')
        # print the top URLs
        fp.write('<ul>\n')
        for data in self.top_urls:
            fp.write(
                '<li>%(count)d '
                '<a class="errurl" href="%(escaped_url)s">'
                '%(escaped_url)s</a> '
                '(%(pageid)s)\n' % data)
            fp.write('<ul class="oops"><li>')
            fp.write(', '.join(
                '<a href="%s">%s</a>' % (get_absolute_url(oops), oops)
                for oops in data['errors'][:self.max_url_errors]))
            fp.write('</li></ul>\n')
            fp.write('</li>\n')
        if self.url_count > self.max_urls:
            fp.write('<li>[%d more]</li>\n'
                     % (self.url_count - self.max_urls))
        fp.write('</ul>\n\n')


class InfestationGroup(AbstractGroup):
    # Assumes it will be passed an oopsinfestation id.

    def __init__(self, oopsinfestation, errors,
                 count, bot_count, local_referrer_count, url_count):
        super(InfestationGroup, self).__init__(
            count, bot_count, local_referrer_count, url_count)
        self.errors = errors.filter(oopsinfestation__exact=oopsinfestation)
        oopsinfestation = Infestation.objects.get(id=oopsinfestation)
        self.etype = oopsinfestation.exception_type
        self.evalue = oopsinfestation.exception_value
        self.bug = oopsinfestation.bug


class MostExpensiveStatementGroup(AbstractGroup):
    # Assumes it will be passed a most_expensive_statement.

    def __init__(self, most_expensive_statement, errors,
                 count, bot_count, local_referrer_count, url_count):
        super(MostExpensiveStatementGroup, self).__init__(
            count, bot_count, local_referrer_count, url_count)
        self.errors = errors.filter(
            most_expensive_statement__exact=most_expensive_statement)
        self.etype = most_expensive_statement
        self.evalue = '' # XXX None

#############################################################################
# Sections


class AbstractSection:

    max_count = None

    def __init__(self, title, errors, max_count=None):
        self.errors = errors
        self.title = title
        self.section_id = title.lower().replace(" ", "-")
        if max_count is not None:
            self.max_count = max_count


class AbstractGroupSection(AbstractSection):

    # Set a class (or define a method) in concrete class.
    group_factory = None
    # Subclass __init__ should define group_count and groups.

    def __init__(self, title, errors, max_count=None, _all_groups=None):
        super(AbstractGroupSection, self).__init__(title, errors, max_count)
        self.error_count = errors.count()
        if _all_groups is not None:
            # This is a convenience for subclasses.  `_all_groups` is not part
            # of the API.
            self.group_count = _all_groups.count()
            self.groups = []
            for group_data in _all_groups[:self.max_count]:
                group_data.update(errors=self.errors)
                self.groups.append(self.group_factory(**group_data))

    def renderHeadlineTXT(self, fp):
        """Render this section stats header in plain text."""
        fp.write(' * %d %s\n' % (self.error_count, self.title))

    def renderHeadlineHTML(self, fp):
        """Render this section stats header in HTML."""
        fp.write('<li><a href="#%s">%d %s</a></li>\n' %
            (self.section_id, self.error_count, self.title))

    def _renderGroups(self, fp, html=False):
        for group in self.groups:
            if html:
                group.renderHTML(fp)
            else:
                group.renderTXT(fp)

    def _limited(self):
        return (self.max_count is not None and
            self.max_count >= 0 and self.group_count > self.max_count)

    def renderTXT(self, fp):
        """Render this section in plain text."""
        if self._limited():
            fp.write('=== Top %d %s (total of %s unique items) ===\n\n' % (
                self.max_count, self.title, self.group_count))
        else:
            fp.write('=== All %s ===\n\n' % self.title)
        self._renderGroups(fp)
        fp.write('\n')

    def renderHTML(self, fp):
        """Render this section in HTML."""
        fp.write('<div id="%s">' % self.section_id)
        if self._limited():
            fp.write('<h2>Top %d %s (total of %s unique items)</h2>\n' % (
                self.max_count, self.title, self.group_count))
        else:
            fp.write('<h2>All %s</h2>\n' % self.title)
        self._renderGroups(fp, html=True)
        fp.write('</div>')


class ErrorSection(AbstractGroupSection):

    group_factory = InfestationGroup

    def __init__(self, title, errors, max_count=None):
        all_groups = (
            errors.values(
                'oopsinfestation').annotate(
                count=Count('oopsid'),
                url_count=Count('url', distinct=True),
                bot_count=SumBool('is_bot'),
                local_referrer_count=SumBool('is_local_referrer')).order_by(
                '-count', 'oopsinfestation__exception_type',
                'oopsinfestation__exception_value')
            )
        super(ErrorSection, self).__init__(
            title, errors, max_count, _all_groups = all_groups)


class NotFoundSection(ErrorSection):
    """Pages Not Found section in the error summary."""

    def __init__(self, title, errors, max_count=None):
        errors = errors.filter(is_local_referrer=True)
        super(NotFoundSection, self).__init__(
            title, errors, max_count)


class TimeOutSection(AbstractGroupSection):
    """Timeout section in the error summary."""

    group_factory = MostExpensiveStatementGroup

    def __init__(self, title, errors, max_count=None):
        all_groups = (
            errors.filter(
                most_expensive_statement__isnull=False).values(
                'most_expensive_statement').annotate(
                count=Count('oopsid'),
                url_count=Count('url', distinct=True),
                bot_count=SumBool('is_bot'),
                local_referrer_count=SumBool('is_local_referrer')).order_by(
                '-count', 'most_expensive_statement')
            )
        super(TimeOutSection, self).__init__(
            title, errors, max_count, _all_groups = all_groups)

# We perform the top value queries outside of the ORM for performance.
#
# 'FROM "oops_oops"' ->
top_value_inner_sql = '''
FROM (
    "oops_oops"
    INNER JOIN (
        %(inner_query)s LIMIT %(max_count)d)
        AS "inner_max"
        ON ("oops_oops".%(field_name)s = "inner_max"."value" AND
            "oops_oops"."pageid" = "inner_max"."pageid"))
'''

class AbstractTopValueSection(AbstractSection):

    max_count = 10
    # Set these.
    field_title = field_name = field_format = None

    def __init__(self, title, errors, max_count=None):
        super(AbstractTopValueSection, self).__init__(
            title, errors, max_count)

        def as_sql(query):
            """XXX Hack to make QuerySet.query.as_sql() work more or less the same.

            Expected behaviour doesn't work on 1.3. See
            http://groups.google.com/group/django-users/browse_thread/thread/a71a7e764f7622a0?pli=1
            """
            return query.get_compiler('default').as_sql()

        # The only way to do this without breaking into SQL means you have to
        # divide up the queries; this way, we do it all in one query, as an
        # optimization.
        # inner_query, inner_args are the necessary SQL to return all the
        # pageids with their top values, ordered by the highest value to the
        # lowest.
        inner_query, inner_args = as_sql(
            self.errors.values_list(
                'pageid').annotate(
                value=Max(self.field_name)).order_by(
                'value', 'pageid').reverse().query)
        # outer_query, outer_args are the necessary SQL to return all the
        # oopsids for the inner_query pageids.  ordered by the highest value
        # to the lowest. PostgreSQL seems to ignore the ordering issued by
        # the inner_query done above.
        outer_query, outer_args = as_sql(
            self.errors.values_list(
                self.field_name, 'oopsid', 'pageid').order_by(
                self.field_name, 'oopsid').reverse().query)
        join_sql = top_value_inner_sql % dict(
            inner_query=inner_query, max_count=self.max_count,
            field_name=connection.ops.quote_name(self.field_name))
        original = ' FROM "oops_oops" '
        assert original in outer_query
        cursor = connection.cursor()
        cursor.execute(
            outer_query.replace(original, join_sql), inner_args + outer_args)
        self.top_errors = []
        for value, oopsid, pageid in cursor.fetchall():
            # If we have multiple oopsids with the same pageid and top
            # value (e.g. same group of OOPSes) then the top value section
            # might end up with multiple instances of the same top value
            # and pageid. Here we store all those OOPSes in a list but
            # self.render* methods display only the first one.
            if not pageid:
                pageid = 'Unknown'
            if self.top_errors and self.top_errors[-1][2] == pageid:
                assert self.top_errors[-1][0] == value, 'programmer error'
                self.top_errors[-1][1].append(oopsid)
            else:
                self.top_errors.append((value, [oopsid], pageid))
        self.top_errors.sort(
            key=lambda error: (error[0], error[2]), reverse=True)

    def renderHeadlineTXT(self, fp):
        return

    def renderHeadlineHTML(self, fp):
        fp.write(
            '<li><a href="#%s">%s</a></li>\n' % (self.section_id, self.title))

    def renderHTML(self, fp):
        fp.write('<div id="%s">' % self.section_id)
        fp.write('<h2>%s</h2>\n' % self.title)
        fp.write('<table class="top-value-table">\n')
        fp.write('<tr>\n')
        fp.write('<th>%s</th>\n' % self.field_title)
        fp.write('<th>Oops ID</th>\n')
        fp.write('<th>Page</th>\n')
        fp.write('</tr>\n')
        for value, oopsids, pageid in self.top_errors:
            fp.write('<tr>\n')
            fp.write('<td>%s</td>\n<td><a href="%s">%s</a></td>'
                     '\n<td>%s</td>\n' % (
                        self.field_format % value,
                        get_absolute_url(oopsids[0]), oopsids[0].encode('utf8'),
                        _escape(pageid)))
            fp.write('</tr>\n')
        fp.write('</table>')
        fp.write('</div>')

    def renderTXT(self, fp):
        fp.write('=== Top %d %s ===\n\n' % (self.max_count, self.title))
        for value, oopsids, pageid in self.top_errors:
            formatted_value = self.field_format % value
            fp.write('%s  %-14s  %s\n' % (formatted_value,
                oopsids[0].encode('utf8'), pageid.encode('utf8')))
        fp.write('\n\n')


class TopDurationSection(AbstractTopValueSection):
    """The top page IDs by duration."""
    title = "Durations"
    field_title = "Duration"
    field_name = 'duration'
    field_format = '%9.2fs'


class StatementCountSection(AbstractTopValueSection):
    """The top statement counts section."""
    title = "Statement Counts"
    field_title = "Count"
    field_name = 'statements_count'
    field_format = '%9d'


class TimeOutCountSection(AbstractSection):
    """The timeout counts by page id section."""

    def renderHeadlineTXT(self, fp):
        pass

    def renderHeadlineHTML(self, fp):
        fp.write(
            '<li><a href="#%s">%s</a></li>\n' % (self.section_id, self.title))

    def renderTXT(self, fp):
        fp.write('=== %s ===\n\n' % (self.title,))
        fp.write('     Hard / Soft  Page ID\n')
        for info in self.time_out_counts:
            fp.write('%(hard_timeouts_count)9s / %(soft_timeouts_count)4s  '
                     '%(pageid)s\n' % info)
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
        for info in self.time_out_counts:
            fp.write('<tr>\n')
            fp.write('<td>%(hard_timeouts_count)s</td>\n'
                     '<td>%(soft_timeouts_count)s</td>\n'
                     '<td>%(pageid)s</td>\n' % info)
            fp.write('</tr>\n')
        fp.write('</table>')
        fp.write('</div>')

    @Lazy
    def time_out_counts(self):
        res = self.errors.filter(
            classification__title__exact='Time Outs').values(
            'pageid').annotate(
            hard_timeouts_count=Count('oopsid')).order_by(
            'hard_timeouts_count').reverse()
        soft_timeouts = dict(
            (d['pageid'], d['soft_timeouts_count']) for d
            in self.errors.filter(
            pageid__in=[d['pageid'] for d in res]).filter(
            classification__title__exact='Soft Time Outs').values(
            'pageid').annotate(
            soft_timeouts_count=Count('oopsid')))
        for info in res:
            info['soft_timeouts_count'] = soft_timeouts.get(info['pageid'], 0)
        # We need to sort by (hard_timeouts_count, soft_timeouts_count),
        # but I don't see how to get both of those at once in the SQL.
        # Therefore, we sort in Python here at the end, assuming that
        # the max_count will keep this group small enough to be cheap.
        # (gary)
        res = sorted(res, key=lambda error: (
            error['hard_timeouts_count'], error['soft_timeouts_count'],
            error['pageid']), reverse=True)
        return res

#############################################################################
# Summaries

_marker = object()

class ErrorSummary:
    """Summary of Oops that happened in a given date [range]. A summary
    is composed by the stats and then the individual error sections.
    """
    #TODO matsubara: maybe stats could be another type of section?

    def __init__(self, start, end, prefixes):
        for date in (start, end):
            if not isinstance(date, datetime.datetime):
                raise TypeError('Dates must be datetime.datetime')
        assert start <= end, 'Bad dates.'
        self.start = start
        self.end = end
        self.period = (end - start).days + 1
        self.prefixes = prefixes
        # When end.time() is 0, we want end's full day worth of data.
        if not end.time():
            end = end + datetime.timedelta(days=1)
        self.errors = Oops.objects.filter(
            date__gte=start, date__lt=end, prefix__value__in=prefixes)
        self.sections = []

    @property
    def count(self):
        """Return the sum of all errors of all sections.

        Count is calculated every time because some sections filter
        out errors, instead of using self.errors count calculated in __init__.
        Top Summary classes (statistics ones) aren't considered as well.
        """
        total_errors = []
        for section in self.sections:
            if not isinstance(section, (AbstractTopValueSection,
                TimeOutCountSection)):
                total_errors.append(section.errors.count())
        return sum(total_errors)

    def get_section_by_id(self, section_id):
        for section in self.sections:
            if section.section_id == section_id:
                return section

    def _get_section_info(self, cls, args, filter=_marker):
        if isinstance(args, basestring):
            args = dict(title=args)
        if filter is _marker:
            filter = dict(classification__title__exact=args['title'])
        return cls, args, filter

    def makeSection(self, cls, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        section = cls(*args, **kwargs)
        return section

    def addSections(self, *data):
        """Add sections to the report applying given filters on errors.

        For each section, represented by a tuple (class, data, filters),
        given filters are applied to the errors, and those are used to build
        the report section.
        """
        for info in data:
            cls, args, filter = self._get_section_info(*info)
            if filter is None:
                errors = self.errors
            else:
                errors = self.errors.filter(**filter)
            args['errors'] = errors
            self.sections.append(self.makeSection(cls, kwargs=args))

    def addExclusiveSection(self, cls, args, data):
        """Add a section to the report excluding all errors of given sections.

        For all the given other sections (each one represented by (class, data,
        filters)), errors are filtered out. At the end, only errors not
        belonging to any other sections remain, and the desired section is
        built with this data.
        """
        cls, args, ignored = self._get_section_info(cls, args)
        errors = self.errors
        for info in data:
            data_cls, data_title, data_filter = self._get_section_info(*info)
            if data_filter is None:
                raise ValueError('exclusive section would be empty')
            errors = errors.exclude(**data_filter)
        args['errors'] = errors
        self.sections.append(self.makeSection(cls, kwargs=args))

    def renderTXT(self, fp):
        fp.write("=== Statistics ===\n\n")
        fp.write(" * Log starts: %s\n" % self.start)
        fp.write(" * Analyzed period: %d days\n" % self.period)
        fp.write(" * Total OOPSes: %d\n" % self.count)
        # Do not print Average OOPS if we have less than a day worth of oops.
        if self.period > 1:
            fp.write(" * Average OOPSes per day: %.2f\n" %
                     (self.count / self.period))
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
                 '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />\n'
                 '<link rel="stylesheet" type="text/css" href="%s/oops/static/oops.css" />\n'
                 '</head>\n'
                 '<body>\n'
                 '<div id=summary>\n'
                 '<h1>Oops Report Summary</h1>\n\n' % settings.ROOT_URL)

        fp.write('<ul id="period">\n')
        fp.write('<li>Log starts: %s</li>\n' % self.start)
        fp.write('<li>Analyzed period: %d days</li>\n' % self.period)
        fp.write('<li>Total exceptions: %d</li>\n' % self.count)
        # Do not print Average OOPS if we have less than a day worth of oops.
        if self.period > 1:
            fp.write('<li>Average exceptions per day: %.2f</li>\n' %
                     (self.count / self.period))
        fp.write('</ul>\n\n')
        fp.write('<ul id="stats">\n')
        for section in self.sections:
            section.renderHeadlineHTML(fp)
        fp.write('</ul>\n\n')

        for section in self.sections:
            fp.write('<a name="%s"></a>' % section.section_id)
            section.renderHTML(fp)

        fp.write('</div>\n')
        fp.write('</body>\n')
        fp.write('</html>\n')


class WebAppErrorSummary(ErrorSummary):
    """Summarize web app error reports"""

    def __init__(self, startdate, enddate, prefixes):
        super(WebAppErrorSummary, self).__init__(startdate, enddate, prefixes)
        self.addSections(
            (TopDurationSection, "Durations", None),
            (StatementCountSection, "Statement Counts", None),
            (TimeOutCountSection, "Time Out Counts by Page ID",
             dict(oopsinfestation__exception_type__in=TIMEOUT_EXCEPTIONS)),
            )
        section_set = (
            (TimeOutSection, 'Time Outs'),
            (TimeOutSection, 'Soft Time Outs'),
            (ErrorSection, 'Informational Only Errors'),
            (ErrorSection, 'User Generated Errors'),
            (ErrorSection, 'Unauthorized Errors'),
            (NotFoundSection, 'Pages Not Found'),
            )
        self.addExclusiveSection(
            ErrorSection, dict(title='Exceptions', max_count=50), section_set)
        self.addSections(*section_set)


class GenericErrorSummary(ErrorSummary):
    """An error summary with only the exception section."""

    def __init__(self, startdate, enddate, prefixes):
        super(GenericErrorSummary, self).__init__(startdate, enddate, prefixes)
        self.addExclusiveSection(
            ErrorSection, dict(title='Exceptions', max_count=50), ())


class CheckwatchesErrorSummary(ErrorSummary):
    """Summarize checkwatches error reports."""

    def __init__(self, startdate, enddate, prefixes):
        super(CheckwatchesErrorSummary, self).__init__(
              startdate, enddate, prefixes)
        section_set = ((ErrorSection, 'Remote Checkwatches Warnings'),)
        self.addExclusiveSection(
            ErrorSection, dict(title='Exceptions', max_count=50), section_set)
        self.addSections(*section_set)


class CodeHostingSummary(ErrorSummary):
    """Summarize errors reports for the code hosting system."""

    def __init__(self, startdate, enddate, prefixes):
        super(CodeHostingSummary, self).__init__(startdate, enddate, prefixes)
        section_set = ((ErrorSection, 'Remote Errors'),)
        self.addExclusiveSection(
            ErrorSection, dict(title='Exceptions', max_count=50), section_set)
        self.addSections(*section_set)


class UbuntuOneErrorSummary(ErrorSummary):
    """Summarize errors reports for Ubuntu One."""

    def __init__(self, startdate, enddate, prefixes):
        super(UbuntuOneErrorSummary, self).__init__(
              startdate, enddate, prefixes)
        section_set = (
            (StatementCountSection, "Statement Counts"),
            (TimeOutSection, 'Time Outs'),
            (ErrorSection, 'Application Errors'),
            (ErrorSection, 'Producer Errors'),
            (ErrorSection, 'Assertion Errors'),
            (ErrorSection, 'Value Errors'),
            (ErrorSection, 'Unknown Errors'),
            )
        self.addExclusiveSection(
            ErrorSection, dict(title='Exceptions', max_count=50), section_set)
        self.addSections(*section_set)

class ISDErrorSummary(GenericErrorSummary):
    """Summarize ISD error reports (placeholder)"""

    def __init__(self, startdate, enddate, prefixes):
        super(ISDErrorSummary, self).__init__(startdate, enddate, prefixes)
