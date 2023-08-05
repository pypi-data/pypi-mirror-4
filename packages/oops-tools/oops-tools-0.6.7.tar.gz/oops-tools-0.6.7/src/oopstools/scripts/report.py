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


import datetime
from email.mime.text import MIMEText
import os
import smtplib

from django.conf import settings

from oopstools.oops import dbsummaries
from oopstools.oops.helpers import parsedate, today
from oopstools.oops.models import Report


# SMTP server instantiated as global so it can be easily replaced by a fake
# one in the test suite.
smtp_server = smtplib.SMTP()


def send_oops_report_email(report, date, body_text):
    # Construct the email.
    msg = MIMEText(body_text, 'plain', 'utf8')
    msg['Subject'] = "%s Errors for %s" % (report.title, date)
    from_addr = "OOPS Summaries <%s>" %  settings.REPORT_FROM_ADDRESS
    msg['From'] = from_addr
    to_addr = report.recipient
    if not to_addr:
        to_addr = settings.REPORT_TO_ADDRESS
    if type(to_addr) is not str:
        to_addr = to_addr.encode('utf8')
    msg['Reply-To'] = to_addr
    msg['To'] = to_addr

    # Send the email.
    smtp_server.connect()
    smtp_server.sendmail(from_addr, to_addr, msg.as_string())
    smtp_server.quit()


def main():
    # For simplicity this script only generates reports for yesterday.
    yesterday = today() - datetime.timedelta(days=1)
    yesterday_string = yesterday.strftime('%Y-%m-%d')

    for report in Report.objects.filter(active=True):
        # Figure out which class to use for the given report.
        summary = getattr(dbsummaries, report.get_summary_display())
        # Prefixes belonging to this report.
        prefixes = [prefix.value for prefix in report.prefixes.all()]
        # Pass yesterday as the start and end to get a full day
        # summary. Use parsedate() because ErrorSummary objects only works
        # with datetime.
        start = end = parsedate(yesterday_string)
        summary = summary(start, end, prefixes)
        if summary.count > 0:
            report_filename = report.name + "-" + yesterday_string
            # Save HTML to disk.
            html_file = open(os.path.join(
                settings.SUMMARY_DIR, report_filename + '.html'), 'wb')
            summary.renderHTML(html_file)
            html_file.close()
            # Save txt to disk.
            txt_file = os.path.join(
                settings.SUMMARY_DIR, report_filename + '.txt')
            fp = open(txt_file, 'wb')
            summary.renderTXT(fp)
            fp.close()
            body_text = (
                'Full summary available at:\n'
                '   %s/%s.html\n\n' % (settings.SUMMARY_URI, report_filename))
            body_text += open(txt_file).read()
        else:
            body_text = "No %s OOPSes found for %s" % (
                report.title, yesterday_string)

        # Send email report
        send_oops_report_email(report, yesterday_string, body_text)
