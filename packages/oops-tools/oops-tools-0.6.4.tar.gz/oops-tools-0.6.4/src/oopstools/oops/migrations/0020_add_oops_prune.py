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

from south.v2 import DataMigration
from south.db import db


class Migration(DataMigration):

    def forwards(self, orm):
        db.create_table('oops_pruneinfo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pruned_until', self.gf('django.db.models.fields.DateTimeField')())
            ))
        db.send_create_signal('oops', ['PruneInfo'])

    def backwards(self, orm):
        db.delete_table('oops_pruneinfo')

    models = {
        'oops.prune': {
            'Meta': {'object_name': 'PruneInfo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pruned_until': ('django.db.models.fields.DateTimeField', [], {}),
        },
    }
    
    complete_apps = ['oops']
