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

# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'PrefixGroup'
        db.create_table('oops_prefixgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('oops', ['PrefixGroup'])

        # Adding field 'Prefix.group'
        db.add_column('oops_prefix', 'group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oops.PrefixGroup'], null=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting model 'PrefixGroup'
        db.delete_table('oops_prefixgroup')

        # Deleting field 'Prefix.group'
        db.delete_column('oops_prefix', 'group_id')
    
    
    models = {
        'oops.appinstance': {
            'Meta': {'object_name': 'AppInstance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'oops.classification': {
            'Meta': {'object_name': 'Classification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'oops.dboopsrootdirectory': {
            'Meta': {'object_name': 'DBOopsRootDirectory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'last_oops': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'root_dir': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'oops.infestation': {
            'Meta': {'unique_together': "(('exception_type', 'exception_value'),)", 'object_name': 'Infestation'},
            'bug': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'exception_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'exception_value': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        },
        'oops.oops': {
            'Meta': {'object_name': 'Oops'},
            'appinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oops.AppInstance']"}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oops.Classification']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'http_method': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'informational': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'is_bot': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'db_index': 'True'}),
            'is_local_referrer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'db_index': 'True'}),
            'most_expensive_statement': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'db_index': 'True'}),
            'oopsid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'oopsinfestation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oops.Infestation']"}),
            'pageid': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'pathname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'prefix': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oops.Prefix']"}),
            'referrer': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True'}),
            'statements_count': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'time_is_estimate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True'}),
            'total_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True', 'db_index': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'})
        },
        'oops.prefix': {
            'Meta': {'object_name': 'Prefix'},
            'appinstance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oops.AppInstance']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oops.PrefixGroup']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'})
        },
        'oops.prefixgroup': {
            'Meta': {'object_name': 'PrefixGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'oops.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
    }
    
    complete_apps = ['oops']
