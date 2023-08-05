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

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^oopstools/', include('oopstools.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'oopstools.oops.views.index'),
    (r'^oops[.py]*/$', 'oopstools.oops.views.index'),
    (r'^prefixloader/$', 'oopstools.oops.views.prefixloader'),
    (r'^reports/(?P<report_name>.*)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d+)/$',
        'oopstools.oops.views.report_day_view'),
    (r'^reports/(?P<report_name>.*)/$', 'oopstools.oops.views.report'),
    (r'^oops[.py]*/meta$', 'oopstools.oops.views.meta'),
    (r'^oops/static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_DOC_ROOT}),
)
