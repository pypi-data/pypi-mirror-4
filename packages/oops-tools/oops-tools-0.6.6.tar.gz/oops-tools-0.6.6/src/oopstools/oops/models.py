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

import bz2
import re
import gzip
import urllib
import urlparse
import datetime
import os.path

from pytz import utc

from django.db import models
from django.db.models.signals import pre_save
import oops_datedir_repo.serializer
from zope.cachedescriptors.property import readproperty

from oopstools.oops.helpers import (
    replace_variables, today, load_prefixes)


oops_re = re.compile(
    r'''
    ^
      (?:(?P<date>\d{4}-\d{2}-\d{2})/)?
      (?:OOPS-)?
      (?P<dse>\d*)
      (?P<oopsprefix>[a-z]+|[a-z]+\d+[a-z]+)
      (?P<id>\d+)
      ,?
    $''', re.IGNORECASE | re.VERBOSE)

# This pattern is intended to match the majority of search engines. I
# built up this list by checking what was accessing
# https://launchpad.net/robots.txt, so it is probably incomplete.  It
# covers the major engines though (Google and Yahoo).
_robot_pat = re.compile(r'''
  Yahoo!\sSlurp               | # main Yahoo spider
  Yahoo-Blogs                 | # Yahoo blog search
  YahooSeeker                 | # Yahoo shopping
  Jakarta\sCommons-HttpClient |
  Googlebot/\d+               | # main Google spider
  Googlebot-Image/\d+         | # Google image search
  PrivacyFinder/\d+           |
  W3C-checklink/\d+           |
  Accoona-AI-Agent/\d+        |
  CE-Preload                  |
  FAST\sEnterprise\sCrawler   |
  Sensis\sWeb\sCrawler        |
  ia_archiver                 | # web.archive.org
  heritrix/\d+                |
  LinkAlarm/d+                |
  rssImagesBot/d+             |
  SBIder/\d+                  |
  HTTrack\s\d+                |
  schibstedsokbot             |
  Nutch\S*/d+                 | # Lucene
  Mediapartners-Google/d+     |
  Miva                        |
  ImagesHereImagesThereImagesEverywhere/d+ |
  DiamondBot                  |
  e-SocietyRobot              |
  Tarantula/\d+               |
  yacy.net                    | # some P2P web index
  penthesila/\d+              |
  asterias/\d+                |
  OpenIntelligenceData/d+     |
  Omnipelagos.com             |
  LinkChecker/\d+             |
  updated/\d+                 |
  VSE/\d+                     |
  Thumbnail.CZ\srobot         |
  SunONERobot/\d+             |
  OutfoxBot/\d+               |
  Ipselonbot/\d+              |
  CsCrawler                   |
  msnbot/\d+                  |
  sogou\sspider               |
  Wget/\d+                    |
  Crawler-PingtheSemanticWeb.com/\d+ |
  MS\sSearch\s\d+.\d+\sRobot
  ''', re.VERBOSE)

MAX_EVALUE_LEN = 1000
MAX_URL_LEN = 500


class OopsReadError(IOError):
    pass


class AppInstance(models.Model):
    """The app instance an oops belongs to."""
    # lpnet, edge, staging, etc.
    title = models.CharField(unique=True, max_length=100)

    def __unicode__(self):
        return unicode(self.title)


class Prefix(models.Model):
    """Oops prefixes as defined by the app instance configuration."""
    value = models.CharField(unique=True, max_length=100)
    appinstance = models.ForeignKey(AppInstance)

    def __unicode__(self):
        return unicode(self.value)


class PruneInfo(models.Model):
    """Information about oops pruning."""
    
    pruned_until = models.DateTimeField()

    @classmethod
    def prune_unreferenced(klass, prune_from, prune_until, references):
        # XXX: This trusts date more than we may want to - should consider
        # having a date_received separate to the date generated.
        while True:
            # There may be very many OOPS to prune, so only ask for a few at a
            # time. This prevents running out of memory in the prune process
            # (can happen when millions of reports are being pruned at once).
            to_delete = set(Oops.objects.filter(
                date__gte=prune_from, date__lte=prune_until).exclude(
                    oopsid__in=references)[:10000])
            # deleting 1 at a time is a lot of commits, but leaves the DB lively
            # for other transactions. May need to batch this in future if its
            # too slow.
            for oopsid in to_delete:
                Oops.objects.filter(oopsid__exact=oopsid).delete()
            if not to_delete:
                break


class Report(models.Model):
    """A summary report for OOPSes of a set of prefixes."""

    SUMMARY_CHOICES = (
        ('webapp', 'WebAppErrorSummary'),
        ('codehosting', 'CodeHostingSummary'),
        ('checkwatches', 'CheckwatchesErrorSummary'),
        ('ubuntuone', 'UbuntuOneErrorSummary'),
        ('isd', 'ISDErrorSummary'),
        ('generic', 'GenericErrorSummary')
    )

    name = models.CharField(unique=True, max_length=20)
    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=20, choices=SUMMARY_CHOICES)
    prefixes = models.ManyToManyField(Prefix)
    active = models.BooleanField(default=False)
    recipient = models.EmailField(max_length=254, null=True)

    def __unicode__(self):
        return unicode(self.name)


class Infestation(models.Model):
    """A group of OOPS reports linked to a bug."""

    bug = models.PositiveIntegerField(null=True)
    exception_type = models.CharField(max_length=100)
    # The exception_value is normalized.  The original exception value
    # for any given OOPS can only be obtained from the OOPS file (see
    # Oops.exception_value).
    exception_value = models.CharField(max_length=MAX_EVALUE_LEN)

    class Meta:
        unique_together = ('exception_type', 'exception_value')

    def __unicode__(self):
        return unicode(self.exception_type)

    @readproperty
    def last_seen_oops(self):
        """Return the last OOPS report with the same infestation."""
        return Oops.objects.filter(oopsinfestation=self).order_by('-date')[0]

    @readproperty
    def past_week_count(self):
        """Return how many OOPSes with the same infestation happened in the
        past week."""
        past_week = today() - datetime.timedelta(days=7)
        # Convert past_week to datetime since OOPS reports use datetime
        # objects.
        past_week = datetime.datetime.combine(past_week, datetime.time())
        return Oops.objects.filter(
            oopsinfestation=self, date__gte=past_week).count()


class Classification(models.Model):
    title = models.CharField(unique=True, max_length=100)


class DBOopsRootDirectory(models.Model):
    """Model to keep the state of an OopsLoader."""
    root_dir = models.CharField(unique=True, max_length=200)
    last_date = models.DateField(null=True)
    last_oops = models.CharField(null=True, max_length=200)


def _get_oops(pathname):
    """Given a pathname to an oopsfile, returns a deserialized OOPS.

    Non-existent file raises OopsReadError.
    """
    try:
        if pathname.lower().endswith('bz2'):
            f = bz2.BZ2File(pathname, 'r')
        elif pathname.lower().endswith('gz'):
            f = gzip.open(pathname, 'r')
        else:
            f = open(pathname, 'r')
        return oops_datedir_repo.serializer.read(f)
    except IOError, e:
        # Couldn't parse, re-raise the exception as an OOPSReadError
        raise OopsReadError("Couldn't read oops report: %s" % e)


def conform(value, maximum=10, splitter=' ... '):
    if len(value) > maximum:
        half = (maximum - len(splitter)) // 2
        value = (value[:half] + splitter + value[-half:])
    return value


_find_and_replace_url = re.compile('https?://[^\s]+').sub


def _normalize_exception_value(etype, evalue, prefix):
    """Return a normalized value.

    Expects an exception type, an exception value and a prefix object.
    """
    # replace pointer values in exception values with a constant
    # string.
    evalue = re.sub("0x[abcdef0-9]+", "INSTANCE-ID", evalue)
    # replace exception value for UnicodeDecodeErrors with a constant
    # string.
    evalue = re.sub(
        "in position [0-9]+-?[0-9]*", "in position INT", evalue)
    # replace exception value for ShortListTimeoutError with a constant
    # string
    evalue = re.sub("There were [0-9]+ items.", "There were INT items.",
                    evalue)
    # Just a convenience because both codehosting and jobs exceptions are
    # processed in the same way.
    codehosting_and_jobs_prefixes = load_prefixes(
        "code") + load_prefixes("jobs")
    if prefix.value in codehosting_and_jobs_prefixes:
        if etype in ['NotBranchError','NoRepositoryPresent']:
            evalue = re.sub(
                '/srv/bazaar.launchpad.net/push-branches.*',
                '/srv/bazaar.launchpad.net/push-branches/BRANCH-PATH',
                evalue)
        elif etype == 'NoSuchFile':
            evalue = re.sub(
                "u'/srv/bazaar.launchpad.net/push-branches[^']*'",
                "u'/srv/bazaar.launchpad.net/push-branches/BRANCH-PATH'",
                evalue)
        elif etype == 'MalformedHunkHeader':
            evalue = re.sub(
                "Malformed hunk header. Does not match format.*",
                "Malformed hunk header. Does not match format.",
                evalue)
    elif prefix.value in load_prefixes("production"):
        if etype in NORMALIZED_EXCEPTIONS:
            evalue = replace_variables(evalue)
    elif prefix.value in load_prefixes("checkwatches"):
        if etype == 'ProtocolError':
            # Replace the URL found in the evalue for a constant.
            evalue = _find_and_replace_url('BUGTRACKER-URL', evalue)
        elif etype == 'Fault':
            evalue = re.sub(
                "Your query returned \d+", "Your query returned INT", evalue)
        elif etype in ["BugNotFound", 'UnparseableBugData']:
            if etype == "UnparseableBugData":
                evalue = _find_and_replace_url('BUGTRACKER-URL', evalue)
            # Replace digits found in the evalue for a constant.
            evalue = re.sub("\d+", "INT", evalue)
    # Crop lengthy evalues
    return conform(evalue, MAX_EVALUE_LEN)


def _get_oops_tuple(oops):
    """Given a deserialized Oops, return a tuple with oops information.

    Return value is a tuple of four parts: a data dictionary of
    Oops information equivalent to the Oops database model, a list of
    request variables, a list of SQL statements, and a traceback string.
    """
    oopsid = oops.get('id')
    prefix = oops.get('reporter')
    if not prefix:
        # Legacy support for pre-reporter using OOPSes.
        prefix_match = oops_re.match(oopsid)
        if prefix_match:
            prefix = prefix_match.group('oopsprefix')
            # Ubuntu One format is prefixZuuid.
            if len(prefix) > 33 and prefix[-33] == 'Z':
                prefix = prefix[:-33]
            elif len(oopsid) >= 37:
                # 37 is len (OOPS-<hash>).
                prefix = None

        if not prefix:
            prefix = 'UNKNOWN'

    prefix = prefix.upper()
    try:
        prefix = Prefix.objects.get(value__exact=prefix)
    except Prefix.DoesNotExist:
        # No known prefix: add it to the system and let sysadmins tweak it
        # later.
        try:
            appinstance = AppInstance.objects.get(title=prefix)
        except AppInstance.DoesNotExist:
            appinstance = AppInstance(title=prefix)
            appinstance.save()
        prefix = Prefix(value=prefix, appinstance=appinstance)
        prefix.save()
    data = dict(
        http_method = 'Unknown',
        referrer = "No referrer",
        user_agent = 'No user agent',
        is_local_referrer = False)
    # Grab data needed by the Oops database model from the req_vars.
    req_vars = oops.get('req_vars') or {}
    # Some badly written OOPSes are tuples with single item tuples. (field.blob
    # was seen).
    # New ones are dicts.
    def ensure_dict(iterable_or_dict):
        try:
            items = iterable_or_dict.items()
            return iterable_or_dict
        except AttributeError:
            result = {}
            for item in iterable_or_dict:
                try:
                    key, value = item
                except ValueError:
                    key = item[0]
                    value = ''
                result[key] = value
            return result
    req_vars = ensure_dict(req_vars)
    for key, value in req_vars.items():
        if isinstance(value, str):
            try:
                # We can get anything in HTTP headers
                # Trying to squeeze the bytes into ASCII plane
                value.decode('ascii')
            except UnicodeDecodeError:
                # If that fails, percent-quote them
                value = urllib.quote(value)
        if key == 'REQUEST_METHOD':
            # Truncate the REQUEST_METHOD if it's longer than 10 characters
            # since a str longer than that is not allowed in the DB.
            data['http_method'] = value[:10]
        elif key == 'HTTP_REFERER':
            data['referrer'] = conform(value, MAX_URL_LEN)
            netloc = urlparse.urlparse(value)[1]
            if (netloc.endswith('launchpad.net') or
                netloc.endswith('ubuntu.com')):
                # It is local.
                data['is_local_referrer'] = True
        elif key == 'HTTP_USER_AGENT':
            data['user_agent'] = conform(value, 200)
    statements = oops.get('timeline') or []
    # Sanity check/coerce the statements into what we expect.
    # Must be a list:
    if not isinstance(statements, list):
        statements = [(0, 0, 'badtimeline', str(statements), 'unknown')]
    else:
        filler = (0, 0, 'unknown', 'unknown', 'unknown')
        for row, action in enumerate(statements):
            statements[row] = tuple(action[:5]) + filler[len(action):]
    duration = oops.get('duration')
    if duration is not None:
        total_time = int(duration * 1000)
        time_is_estimate = False
    elif not statements:
        total_time = 0
        time_is_estimate = True # '(estimate)'
    else:
        total_time = statements[-1][1]
        time_is_estimate = True
    # Some scripts have duration: -1, so for all it's worth, let's make those
    # equal 0.
    if total_time < 0:
        total_time = 0
    # Get the oops infestation
    exception_type = oops.get('type') or ''
    exception_value = oops.get('value') or ''
    exception_value = _normalize_exception_value(
        exception_type, exception_value, prefix)
    try:
        infestation = Infestation.objects.get(
            exception_type__exact=exception_type,
            exception_value__exact=exception_value)
    except Infestation.DoesNotExist:
        infestation = Infestation(
            exception_type=exception_type,
            exception_value=exception_value)
        infestation.save()
    # most_expensive_statement
    if not statements:
        most_expensive_statement = None
    else:
        costs = {}
        for (start, end, db_id, statement, tb) in statements:
            statement = replace_variables(statement)
            cost = end - start
            if statement in costs:
                costs[statement] += cost
            else:
                costs[statement] = cost
        costs = sorted((cost, statement)
                       for (statement, cost) in costs.items())
        most_expensive_statement = costs[-1][1]
    # Trim most_expensive_statements to 200 characters
    if most_expensive_statement is not None:
        most_expensive_statement = conform(most_expensive_statement, 200)
    url = oops.get('url') or ''
    if type(url) is unicode:
        # We have gotten a ringer, URL's are bytestrings. Encode to UTF8 to get
        # a bytestring and urllib.quote to get a url.
        url = urllib.quote(url.encode('utf8'))
    else:
        try:
            url.decode('ascii')
        except UnicodeDecodeError:
            # The URL is not ASCII and thus definitely not a URL.
            # There may be a byte in local encoding or it may be UTF8 - we need
            # to quote it to make it a valid URL - this is better than
            # rejecting the OOPS, or having a URL that isn't in the DB.
            url = urllib.quote(url)
    url = conform(url, MAX_URL_LEN)

    informational = oops.get('informational', 'False').lower() == 'true'
    oops_date = oops.get('time')
    if oops_date is None:
        oops_date = datetime.datetime.now(utc)
    data.update(
        oopsid = oopsid,
        prefix = prefix,
        date = oops_date.replace(microsecond=0),
        # Missing topics are '' which will group all such reports together in
        # some ways, but thats tolerable vs something (near) unique like url:
        # that prevents aggregation.
        pageid = oops.get('topic') or '',
        url = url,
        duration = duration,
        informational = informational,
        total_time = total_time,
        time_is_estimate = time_is_estimate,
        oopsinfestation = infestation,
        most_expensive_statement = most_expensive_statement,
        is_bot = _robot_pat.search(data['user_agent']) is not None,
        statements_count = len(statements),
        )
    return (
        data, sorted(req_vars.items()), statements, oops.get('tb_text') or '')


def parsed_oops_to_model_oops(parsed_oops, pathname):
    """Convert an oops report dict to an Oops object."""
    data, req_vars, statements, traceback = _get_oops_tuple(parsed_oops)
    data['pathname'] = pathname
    res = Oops(**data)
    res.appinstance = res.get_appinstance()
    res.save()
    # Get it again.  Otherwise we have discrepancies between old and
    # new oops objects: old ones have unicode attributes, and new
    # ones have string attributes, for instance.  Ideally the message
    # conversion would have converted everything to unicode, but it
    # doesn't easily.
    res = Oops.objects.get(oopsid__exact=parsed_oops['id'])
    res.parsed_oops = parsed_oops
    res.req_vars = req_vars
    res.statements = statements
    res.traceback = traceback
    res.save()
    return res


class Oops(models.Model):
    """An OOPS report."""
    oopsinfestation = models.ForeignKey(Infestation, db_index=True)
    pathname = models.CharField(max_length=200, unique=True)
    oopsid = models.CharField(max_length=200, unique=True)
    prefix = models.ForeignKey(Prefix, db_index=True)
    pageid = models.CharField(max_length=MAX_URL_LEN)
    date = models.DateTimeField('date', db_index=True)
    url = models.URLField(null=True, db_index=True, max_length=MAX_URL_LEN)
    http_method = models.CharField(null=True, max_length=10)
    statements_count = models.PositiveIntegerField(null=True)
    duration = models.FloatField(null=True)
    referrer = models.URLField(null=True, max_length=MAX_URL_LEN)
    user_agent = models.CharField(max_length=200, null=True)
    most_expensive_statement = models.CharField(
        max_length=200, null=True, db_index=True)
    branch_nick = models.CharField(max_length=200, null=True)
    revno = models.PositiveIntegerField(null=True)
    total_time = models.PositiveIntegerField()
    time_is_estimate = models.NullBooleanField()
    informational = models.NullBooleanField()
    appinstance = models.ForeignKey(AppInstance)
    is_bot = models.NullBooleanField(db_index=True)
    is_local_referrer = models.NullBooleanField(db_index=True)
    classification = models.ForeignKey(
        Classification, db_index=True, null=True)
    statements_count = models.PositiveIntegerField()

    def __unicode__(self):
        return unicode(self.oopsid)

    @property
    def branch_nick(self):
        return self.parsed_oops.get('branch_nick', 'Unknown') or 'Unknown'

    @property
    def revno(self):
        return self.parsed_oops.get('revno', 'Unknown')

    @property
    def userdata(self):
        return self.parsed_oops.get('username', '')

    @classmethod
    def from_pathname(cls, pathname):
        parsed_oops = _get_oops(pathname)
        oopsid = parsed_oops.get('id')
        if oopsid is None:
            raise OopsReadError('Not a valid OOPS report')
        try:
            res = cls.objects.get(oopsid__exact=oopsid)
        except cls.DoesNotExist:
            res = parsed_oops_to_model_oops(parsed_oops, pathname)
        return res

    @readproperty
    def parsed_oops(self):
        self.parsed_oops = _get_oops(self.pathname)
        return self.parsed_oops

    @readproperty
    def hostname(self):
        # Currently from oops reports only.
        return self.parsed_oops.get('hostname', 'Unknown') or 'Unknown'

    def _set_values(self):
        ignore, self.req_vars, self.statements, self.traceback = (
            _get_oops_tuple(self.parsed_oops))

    @readproperty
    def req_vars(self):
        self._set_values()
        return self.req_vars

    @readproperty
    def statements(self):
        self._set_values()
        return self.statements

    @readproperty
    def traceback(self):
        self._set_values()
        return self.traceback

    @property
    def exception_type(self):
        return self.oopsinfestation.exception_type

    @property
    def exception_value(self):
        return self.parsed_oops.get('value')

    @property
    def normalized_exception_value(self):
        return self.oopsinfestation.exception_value

    def get_appinstance(self):
        """Return the AppInstance this OOPS belongs to."""
        return self.prefix.appinstance

    def exists(self):
        """Return True if pathname exists in the filesystem."""
        return os.path.exists(self.pathname)

    def formatted_statements(self):
        #XXX need docstring and test
        if not self.statements:
            return []
        return [(count+1, start, stop, db_id, stop - start, stmt, tb) for
                (count, (start, stop, db_id, stmt, tb)) in
                enumerate(self.statements)]

    def repeated_statements(self):
        """Return a list of repeated SQL statements."""
        groupedstatements = sorted(self._group_queries(self.statements),
            key=lambda (gtime, count, mean_length, saving, db_id, statement):
            (-int(count), -int(saving)))
        repeated_stmt = []
        projected_total_time = self.total_time
        for idx, (gtime, count, mean_length, saving, db_id, statement) in (
            enumerate(groupedstatements)):
            # XXX
            if saving:
                projected_total_time -= saving
                repeated_stmt.append((idx+1, count, gtime, int(mean_length),
                    saving, db_id, projected_total_time, statement))
        return repeated_stmt

    def longest_statements(self):
        """Return a list of longest SQL statements."""
        longstatements = sorted(self._group_queries(self.statements),
            key=lambda (gtime, count, mean_length, saving, db_id, statement):
            -mean_length)
        longest_stmt = []
        for idx, (gtime, count, mean_length, saving, db_id, statement) in (
            enumerate(longstatements)):
            # XXX
            longest_stmt.append((idx+1, mean_length, count, db_id, statement))
        return longest_stmt

    @property
    def bug(self):
        """Return bug number associated with this OOPS."""
        return self.oopsinfestation.bug

    @property
    def user(self):
        """Return display name parsed from self.userdata."""
        user = self.userdata.split(",")
        return user[-1].strip()

    @property
    def user_db_id(self):
        """Return user DB id parsed from self.userdata."""
        db_id = self.userdata.split(",")
        if len(db_id) < 2:
            return None
        return db_id[1].strip()

    @property
    def accumulated_time(self):
        """Return time in miliseconds spent executing SQL queries."""
        if not self.statements:
            return 0
        accumulated_time = 0
        for (start, stop, db_id, stmt, trace) in self.statements:
            length = stop - start
            accumulated_time += length
        return accumulated_time

    @property
    def total_non_sql_time(self):
        """Return time in miliseconds spent running code outside of the DB."""
        return self.total_time - self.accumulated_time

    def _group_queries(self, unsorted_statements):
        """Group SQL log queries.

        unsorted_statements is a list of (start, stop, db_id, statement, tb).
        Return a list of (total_time_ms, count, mean_length, saving, db_id,
        statement).
        """
        sorted_statements = sorted(
            unsorted_statements,
            key=lambda row: row[3]
            )
        groups = []
        def append_to_group(gtime, gcount, db_id, statement):
            mean_length = float(group_time) / float(group_count)
            time_saved = gtime - int(mean_length)
            groups.append((
                gtime, gcount, mean_length, time_saved, db_id, statement))

        group_statement = None
        for row in sorted_statements:
            start, stop, db_id, statement, tb = row
            statement = replace_variables(statement)
            length = stop - start
            if statement != group_statement:
                if group_statement is not None:
                    append_to_group(
                        group_time, group_count, db_id, group_statement)
                group_time = length
                group_statement = statement
                group_count = 1
            else:
                group_time += length
                group_count += 1

        if group_statement is not None:
            append_to_group(group_time, group_count, db_id, group_statement)

        return groups

    def isBot(self): # XXX legacy
        """Does oops.user_agent in the Oops match the robot pattern?
        """
        return self.is_bot



#############################################################################
# XXX This is LP-specific.  To make the OOPS tools generically useful, we
# should put this somewhere else LP-specific.

NORMALIZED_EXCEPTIONS = (
    'RequestExpired', 'ProgrammingError',
    'SQLObjectMoreThanOneResultError', 'RequestStatementTimedOut',
    'TimeoutError', 'LaunchpadTimeoutError')

HARD_TIMEOUT_EXCEPTIONS = ['RequestExpired',
                           'RequestStatementTimedOut',
                           'TimeoutError',
                           'LaunchpadTimeoutError']
SOFT_TIMEOUT_EXCEPTIONS = ['SoftRequestTimeout']
TIMEOUT_EXCEPTIONS = HARD_TIMEOUT_EXCEPTIONS + SOFT_TIMEOUT_EXCEPTIONS
USER_GENERATED_EXCEPTIONS = ['UnexpectedFormData',
                             'OffsiteFormPostError',
                             'ProtocolErrorException',
                             'InvalidBatchSizeError',
                             'UnsupportedFeedFormat',
                             'UntrustedReturnURL',
                             'UserRequestOops']
CODEHOSTING_EXCEPTIONS = ["ConnectionError",
                          "InvalidHttpResponse",
                          "TimeoutError",
                          "NotBranchError",
                          "UnsupportedFormatError",
                          "UnknownFormatError",
                          "BranchReferenceForbidden",
                          "BranchReferenceValueError",
                          "BranchReferenceLoopError",
                          "InvalidURIError"]


def _is_non_ascii(url):
    """Return True if url contains non-ascii characters"""
    try:
        urllib.unquote(url).encode('ascii')
    except UnicodeError:
        return True
    else:
        return False

def classifier(sender, instance, **kwargs):
    if instance.classification is not None:
        return
    match = None
    etype = instance.oopsinfestation.exception_type
    # Start with codehosting because a TimeoutError for codehosting means
    # it's a remote error.
    if (instance.prefix.value in load_prefixes("code") and
        etype in CODEHOSTING_EXCEPTIONS):
        match = 'Remote Errors'
    elif etype in HARD_TIMEOUT_EXCEPTIONS:
        match = 'Time Outs'
    elif etype in SOFT_TIMEOUT_EXCEPTIONS:
        match = 'Soft Time Outs'
    elif instance.informational:
        match = 'Informational Only Errors'
    elif (etype in USER_GENERATED_EXCEPTIONS or
          (etype in ['UnicodeEncodeError',
                     'TypeError',
                     'ProgrammingError'] and
           ('@@' in instance.url or _is_non_ascii(instance.url)))):
        match = 'User Generated Errors'
    elif etype == 'Unauthorized':
        match = 'Unauthorized Errors'
    elif etype in ['NotFound', 'DeletedProxiedLibraryFileAlias', 'GoneError']:
        match = 'Pages Not Found'
    elif (instance.prefix.value in load_prefixes("checkwatches") and
          etype in ["BugTrackerConnectError", "BugWatchUpdateWarning",
                   "UnknownRemoteStatusError", "InvalidBugId",
                   "BugNotFound"]):
        match = 'Remote Checkwatches Warnings'
    if match is not None and (
        instance.classification is None or
        instance.classification.title != match):
        # Set the instance's classification.
        instance.classification = Classification.objects.get(title=match)

pre_save.connect(classifier, sender=Oops)
