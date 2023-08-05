# Copyright 2009-2011 Canonical Ltd.  All rights reserved.
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

from django.contrib import admin

from oopstools.oops.models import Infestation, Oops, Prefix, Report


class OopsAdmin(admin.ModelAdmin):
    list_display = ('oopsid', 'oopsinfestation')


class InfestationAdmin(admin.ModelAdmin):
    list_display = (
        'bug', 'exception_type', 'exception_value')


class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'title', 'summary', 'active')
    filter_horizontal = ('prefixes',)


class PrefixAdmin(admin.ModelAdmin):
    list_display = ('value', 'appinstance')


admin.site.register(Oops)
admin.site.register(Infestation, InfestationAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Prefix, PrefixAdmin)
