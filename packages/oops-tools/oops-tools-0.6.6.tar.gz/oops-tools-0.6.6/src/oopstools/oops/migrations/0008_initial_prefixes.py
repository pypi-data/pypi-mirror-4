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

from string import ascii_uppercase

from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        """Data migration for OOPS prefixes.

        This data migration adds all prefixes needed by oops-tools tests.
        """
        appinstances_dict = {
            'staging': ["S", "X"]
            }

        for appinstance in appinstances_dict.keys():
            for prefix in appinstances_dict[appinstance]:
                a = orm.AppInstance.objects.get(title=appinstance)
                # If the prefix doesn't exist in the database, then add it.
                # This is to cope with the data already in the database added
                # by the previous mechanism using initial_data.json
                try:
                    p = orm.Prefix.objects.get(value=prefix)
                except orm.Prefix.DoesNotExist:
                    p = orm.Prefix(value=prefix, appinstance=a)
                p.save()

    def backwards(self, orm):
        raise RuntimeError("Can not reverse this migration.")

    models = {
        'oops.appinstance': {
            'Meta': {'object_name': 'AppInstance'},
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '50'})
        },
        'oops.classification': {
            'Meta': {'object_name': 'Classification'},
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '100'})
        },
        'oops.dboopsrootdirectory': {
            'Meta': {'object_name': 'DBOopsRootDirectory'},
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
            'last_date': ('django.db.models.fields.DateField', [],
                {'null': 'True'}),
            'last_oops': ('django.db.models.fields.CharField', [],
                {'max_length': '200', 'null': 'True'}),
            'root_dir': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '200'})
        },
        'oops.infestation': {
            'Meta': {'unique_together':
                "(('exception_type', 'exception_value'),)",
                'object_name': 'Infestation'},
            'bug': ('django.db.models.fields.PositiveIntegerField', [],
                {'null': 'True'}),
            'exception_type': ('django.db.models.fields.CharField', [],
                {'max_length': '100'}),
            'exception_value': ('django.db.models.fields.CharField', [],
                {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
        },
        'oops.oops': {
            'Meta': {'object_name': 'Oops'},
            'appinstance': ('django.db.models.fields.related.ForeignKey', [],
                {'to': "orm['oops.AppInstance']"}),
            'classification': ('django.db.models.fields.related.ForeignKey', [],
                {'to': "orm['oops.Classification']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [],
                {'db_index': 'True'}),
            'duration': ('django.db.models.fields.FloatField', [],
                {'null': 'True'}),
            'http_method': ('django.db.models.fields.CharField', [],
                {'max_length': '10', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
            'informational': ('django.db.models.fields.NullBooleanField', [],
                {'null': 'True'}),
            'is_bot': ('django.db.models.fields.NullBooleanField', [],
                {'null': 'True', 'db_index': 'True'}),
            'is_local_referrer': ('django.db.models.fields.NullBooleanField', [],
                {'null': 'True', 'db_index': 'True'}),
            'most_expensive_statement': ('django.db.models.fields.CharField', [],
                {'max_length': '200', 'null': 'True', 'db_index': 'True'}),
            'oopsid': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '200'}),
            'oopsinfestation': ('django.db.models.fields.related.ForeignKey', [],
                {'to': "orm['oops.Infestation']"}),
            'pageid': ('django.db.models.fields.CharField', [],
                {'max_length': '500'}),
            'pathname': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '200'}),
            'prefix': ('django.db.models.fields.related.ForeignKey', [],
                {'to': "orm['oops.Prefix']"}),
            'referrer': ('django.db.models.fields.URLField', [],
                {'max_length': '500', 'null': 'True'}),
            'statements_count': ('django.db.models.fields.PositiveIntegerField', [],
                {}),
            'time_is_estimate': ('django.db.models.fields.NullBooleanField', [],
                {'null': 'True'}),
            'total_time': ('django.db.models.fields.PositiveIntegerField', [],
                {}),
            'url': ('django.db.models.fields.URLField', [],
                {'max_length': '500', 'null': 'True', 'db_index': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [],
                {'max_length': '200', 'null': 'True'})
        },
        'oops.prefix': {
            'Meta': {'object_name': 'Prefix'},
            'appinstance': ('django.db.models.fields.related.ForeignKey', [],
                {'to': "orm['oops.AppInstance']"}),
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '20'})
        },
        'oops.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [],
                {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [],
                {'unique': 'True', 'max_length': '200'})
        },
    }

    complete_apps = ['oops']
