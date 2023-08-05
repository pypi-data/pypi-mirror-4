# Copyright 2011 Canonical Ltd.  All rights reserved.
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

from django.db import models
from south.v2 import DataMigration
from south.db import db


class Migration(DataMigration):

    def forwards(self, orm):
        db.alter_column('oops_prefix', 'value', models.CharField(unique=True, max_length=100))
        db.alter_column('oops_appinstance', 'title', models.CharField(unique=True, max_length=100))

    def backwards(self, orm):
        db.alter_column('oops_prefix', 'value', models.CharField(unique=True, max_length=20))
        db.alter_column('oops_appinstance', 'title', models.CharField(unique=True, max_length=50))
