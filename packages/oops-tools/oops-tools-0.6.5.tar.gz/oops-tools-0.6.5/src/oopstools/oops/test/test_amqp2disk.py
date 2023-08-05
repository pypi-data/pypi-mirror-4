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

import bson
from fixtures import TempDir
from testtools import TestCase

from oopstools.oops.models import Oops
from oopstools.scripts import amqp2disk


class TestOOPSConfig(TestCase):

    def test_publishes_disk_and_DB(self):
        self.root_dir = self.useFixture(TempDir()).path
        config = amqp2disk.make_amqp_config(self.root_dir)
        orig_report = {'id': '12345'}
        report = dict(orig_report)
        ids = config.publish(report)
        self.assertEqual(['12345', '12345'], ids)
        with open(report['datedir_repo_filepath'], 'rb') as fp:
            disk_report = bson.loads(fp.read())
        self.assertEqual(disk_report, orig_report)
        model_report = Oops.objects.get(oopsid='12345')
        self.assertNotEqual(None, model_report)
