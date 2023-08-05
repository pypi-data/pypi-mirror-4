#!/usr/bin/env python
#
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
#
# This script generates a report for production, qastaging and staging for the
# last hour worth of oops reports.

from datetime import datetime, timedelta
import os

from django.conf import settings

from oopstools.oops import dbsummaries
from oopstools.oops.models import Report


def main():
    reports = ['production', 'qastaging', 'staging']
    for report in Report.objects.filter(name__in=reports):
        # Figure out which class to use for the given report.
        summary = getattr(dbsummaries, report.get_summary_display())
        # Prefixes belonging to this report.
        prefixes = [prefix.value for prefix in report.prefixes.all()]
        # Only the last hour worth of reports.
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        summary = summary(last_hour, now, prefixes)
        report_filename = report.name + "-last-hour.txt"
        # Save txt file to disk, so it can be used by lp-stats
        txt_file = open(os.path.join(
            settings.SUMMARY_DIR, report_filename), 'wb')
        summary.renderTXT(txt_file)
