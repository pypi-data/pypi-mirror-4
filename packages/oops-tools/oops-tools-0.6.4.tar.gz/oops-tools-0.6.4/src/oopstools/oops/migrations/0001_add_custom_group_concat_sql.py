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
from south.db import db
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Note that Postgres does not support GROUP_CONCAT directly and needs
        # to emulate it.
        # Stuart suggests:
        # <stub> http://www.postgresql.org/docs/current/static/xaggr.html has
        # the array_accum aggregate function, which can be combined with
        # array_to_string at
        # http://www.postgresql.org/docs/8.4/static/functions-array.html to do
        # something similar.
        # <stub> ie. array_to_string(array_accum(foo),',') should be
        # equivalent to group_concat(foo)
        #
        # Since this custom SQL is run by automatically when running
        # migrations, we first need to drop the AGGREGATE and the FUNCTION 
        # before trying to CREATE a new one.
        db.execute("DROP AGGREGATE IF EXISTS GROUP_CONCAT(text);")
        db.execute("DROP FUNCTION IF EXISTS comma_array_to_string(text[]);")
        db.execute("CREATE FUNCTION comma_array_to_string(text[]) RETURNS text AS $$ SELECT array_to_string($1,','); $$ LANGUAGE SQL;")
        db.execute("""CREATE AGGREGATE GROUP_CONCAT(text)
            (
                sfunc = array_append,
                stype = text[],
                finalfunc = comma_array_to_string,
                initcond = '{}'
            );""")

    def backwards(self, orm):
        pass
