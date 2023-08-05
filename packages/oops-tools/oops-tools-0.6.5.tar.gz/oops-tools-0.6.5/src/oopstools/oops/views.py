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

import os.path

from datetime import datetime, timedelta

from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response

from oopstools.oops import dbsummaries
from oopstools.oops.helpers import parsedate
from oopstools.oops.models import Oops, Report
from oopstools.oops.prefixloader import PrefixLoader
from oopstools.oops.oopsstore import OopsStore, OopsNotFound


def index(request):
    # For any OOPS we search for:
    # - the literal string
    # - an upper() version of the string in case it was previously upper cased
    # on insertion into the DB.
    # - a lower() version of the string in case it wasn't upper cased but the
    # user's reporting tool has upper cased it.
    # - those three things with OOPS- prefixed, if they do not have that prefix
    # already in case the url the user was given had had the OOPS- prefixed
    # removed for some unknown reason, and the report has an OOPS- prefix in
    # its id.
    query_str = request.GET.get('oopsid', '')
    oopsids = set([query_str])
    oopsids.add(query_str.upper())
    oopsids.add(query_str.lower())
    if not query_str.upper().startswith('OOPS-'):
        oopsids.update(map(lambda x:'OOPS-'+x, oopsids))

    # Check each ID in both the database and filesystem
    # (should maybe have an API option for this, instead of doing it manually?)
    try:
        oops = Oops.objects.get(oopsid__in=oopsids)
    except Oops.DoesNotExist:
        # Try to find the OOPS report in the filesystem.
        oops = None
        store = OopsStore(settings.OOPSDIR)
        for oopsid in oopsids:
            try:
                oops = store.find_oops(oopsid)
                break
            except OopsNotFound:
                pass

    if oops and oops.exists():
        tmpl = "oops.html"
        data = {
            'oops': oops
        }
    else:
        tmpl = settings.INDEX_TEMPLATE
        reports = Report.objects.filter(active=True)
        data = {
            'userdata': request.GET,
            'reports': reports
        }
    return render_to_response(tmpl, dictionary=data)


def meta(request):
    bug_number = request.POST.get('bug_number', '')
    oopsid = request.POST.get('oopsid')
    oops = Oops.objects.get(oopsid__exact=oopsid)
    oops.oopsinfestation.bug = bug_number
    oops.oopsinfestation.save()
    return HttpResponseRedirect('/oops.py/?oopsid=%s' % oopsid)


def prefixloader(request):
    prefixes = None
    if request.method == "POST":
        prefixloader = PrefixLoader(settings.LAZR_CONFIG)
        prefixes = prefixloader.load_prefixes_into_database()

    return render_to_response("prefixloader.html", dictionary={
        "LAZR_CONFIG": settings.LAZR_CONFIG,
        "prefixes": prefixes})


def report(request, report_name):
    try:
        r = Report.objects.get(name=report_name, active=True)
    except Report.DoesNotExist:
        raise Http404
    else:
        # Since reports are created by an external script, let's build URLs
        # for the past ten days.
        now = datetime.utcnow()
        dates = []
        for day in range(1, 11):
            dates.append(now - timedelta(day))
        data = {
            'report': r,
            'dates': dates,
            'SUMMARY_URI': settings.SUMMARY_URI,
            }
        return render_to_response("report.html", dictionary=data)


def report_day_view(request, report_name, year, month, day):
    filename = '-'.join([report_name, year, month, day]) + '.html'
    # Try to find out if the report exists already.
    if os.path.exists(os.path.join(settings.SUMMARY_DIR, filename)):
        url = settings.SUMMARY_URI + '/' + filename
        return HttpResponseRedirect(url)
    else:
        # Build it dynamically. This might take some time...
        try:
            report = Report.objects.get(name=report_name, active=True)
        except Report.DoesNotExist:
            raise Http404
        else:
            summary_class = getattr(dbsummaries, report.get_summary_display())
            prefixes = [prefix.value for prefix in report.prefixes.all()]
            start = end = parsedate("-".join([year, month, day]))
            # XXX Unpack the data needed from the summary object to avoid
            # doing processing in the template.
            # There's probably a better way of doing this.
            summary = summary_class(start, end, prefixes)
            durations_section = summary.get_section_by_id('durations')
            stmt_counts_section = summary.get_section_by_id(
                'statement-counts')
            timeout_counts = summary.get_section_by_id(
                'time-out-counts-by-page-id')
            data = {
                'ROOT_URL': settings.ROOT_URL,
                'summary': summary,
                'durations': durations_section,
                'stmt_counts': stmt_counts_section,
                'timeout_counts': timeout_counts
                }
            return render_to_response("summary.html", dictionary=data)



