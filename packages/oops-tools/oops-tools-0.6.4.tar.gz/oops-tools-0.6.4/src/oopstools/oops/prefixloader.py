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


import re
import os
import os.path

from ConfigParser import MissingSectionHeaderError

from django.conf import settings
from lazr.config import ConfigSchema
from lazr.config.interfaces import NoConfigError

from oopstools.oops.models import AppInstance, Prefix


class PrefixLoader:
    """Load OOPS prefixes into the database from a lazr.config file or dir."""

    def __init__(self, lazr_config):
        """Initialize the loader from the lazr.config file or dir."""
        self._schemas = []
        if os.path.isfile(lazr_config):
            self._schemas.append(ConfigSchema(lazr_config))
        elif os.path.isdir(lazr_config):
            config_files = []
            for root, dirs, files in os.walk(lazr_config):
                for filename in files:
                    if filename.endswith('.conf'):
                        config_files.append(os.path.join(root, filename))
            for config_file in config_files:
                try:
                    self._schemas.append(ConfigSchema(config_file))
                except MissingSectionHeaderError:
                    # Oops, not a lazr.config file, go to the next one.
                    continue
        else:
            raise NoConfigError
        self._prefixes = []
        for schema in self._schemas:
            self._prefixes.extend(self._get_prefixes(schema))

    def _get_appinstance_from_schema(self, schema):
        """Figure out AppInstance from the lazr.conf filename."""
        # Remove the common part from the filename.
        appinstance_and_conf_file = re.sub(
            settings.LAZR_CONFIG, '', schema.filename)
        # Remove the .conf part of the filename.
        appinstance = appinstance_and_conf_file.replace(schema.name, '')
        # Remove trailing slash, if any.
        appinstance = appinstance.replace('/', '')
        if not appinstance:
            return ''
        else:
            # Remove the digit from the appinstance (e.g. edge1, edge2, etc).
            appinstance = re.sub('\d', '', appinstance)
            return appinstance

    def _get_prefixes(self, schema):
        """Return prefixes for a given ConfigSchema object."""
        prefixes = []
        for section in schema:
            appinstance = self._get_appinstance_from_schema(schema)
            for key in section:
                if key == 'oops_prefix':
                    prefixes.append((appinstance, section['oops_prefix']))
        return prefixes

    def iter_prefixes(self):
        """Return a list of prefixes found in the lazr.config file(s)."""
        return [prefix for (appinstance, prefix) in self._prefixes]

    def load_prefixes_into_database(self):
        """Load prefixes into the database."""
        prefixes = []
        for appinstance, prefix in self._prefixes:
            try:
                prefix = Prefix.objects.get(value=prefix)
            except Prefix.DoesNotExist:
                try:
                    appinstance = AppInstance.objects.get(title=appinstance)
                except AppInstance.DoesNotExist:
                    appinstance = AppInstance(title=appinstance)
                    appinstance.save()
                prefix = Prefix(value=prefix, appinstance=appinstance)
                prefix.save()
                prefixes.append(prefix.value)
        # Stabilize the order so we can reliably test the return value.
        return sorted(prefixes)
