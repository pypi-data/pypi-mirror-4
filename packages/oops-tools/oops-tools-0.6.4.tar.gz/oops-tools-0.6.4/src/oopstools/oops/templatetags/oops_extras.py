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

from urllib import urlencode
from urlparse import urlparse, urlunparse

from django import template
from django.conf import settings

import sqlparse

register = template.Library()


@register.filter
def topvalueformat(value, field_format):
    return "%s" % field_format % value


@register.filter
def sub(value, arg):
    return int(value) - int(arg)

@register.filter
def div(value, arg):
    return int(value) / int(arg)

@register.filter
def format_sql(raw_sql):
    return sqlparse.format(
        raw_sql,
        keyword_case="upper",
        identfier_case="lower",
        strip_comments=False,
        reindent=True,
        indent_tabs=False)

@register.filter
def get_absolute_url(oopsid):
    """Return the URL for the given oops id."""
    scheme, netloc = urlparse(settings.ROOT_URL)[:2]
    path = 'oops'
    query_string = urlencode({'oopsid': oopsid})
    return urlunparse((scheme, netloc, path, '', query_string, ''))
