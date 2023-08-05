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


from datetime import (
    datetime,
    )
from cStringIO import StringIO
import uuid

from pytz import utc
from testtools import TestCase
from testtools.matchers import Contains

from oopstools.oops.dbsummaries import WebAppErrorSummary
from oopstools.oops.models import parsed_oops_to_model_oops


class TestWebAppErrorSummary(TestCase):

    def _createOops(self):
        python_oops = {
            'id': uuid.uuid4().get_hex(),
            'reporter': 'edge',
            'type': 'Exception',
            'value': u'a unicode char (\xa7)',
            'time': datetime(2008, 1, 13, 23, 14, 23, 00, utc),
            'topic': u'more unicode \xa7',
            }
        ignored = parsed_oops_to_model_oops(
            python_oops, str(self.id()))

    def setUp(self):
        super(TestWebAppErrorSummary, self).setUp()
        self._createOops()
        start = end = datetime(2008, 1, 13)
        prefixes = ['EDGE']
        self.summary = WebAppErrorSummary(start, end, prefixes)

    def test_renderHTML_with_unicode_data(self):
        # Summarising an oops with a unicode exception value should output
        # a UTF-8 encoded html representation.
        fp = StringIO()
        self.summary.renderHTML(fp)
        self.assertThat(fp.getvalue(), Contains('a unicode char (\xc2\xa7)'))
        self.assertThat(fp.getvalue(), Contains('more unicode \xc2\xa7'))

    def test_renderTXT_with_unicode_data(self):
        # Summarising an oops with a unicode exception value should output
        # a UTF-8 encoded text representation.
        fp = StringIO()
        self.summary.renderTXT(fp)
        self.assertThat(fp.getvalue(), Contains('a unicode char (\xc2\xa7)'))
        self.assertThat(fp.getvalue(), Contains('more unicode \xc2\xa7'))
