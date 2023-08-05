#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008-2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

"""
Settings for administration pages
"""
import datetime

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
try:
    from chimere import tasks
except ImportError:
    pass

from chimere.forms import MarkerAdminForm, RouteAdminForm, AreaAdminForm,\
                          NewsAdminForm, CategoryAdminForm, ImporterAdminForm, \
                          PictureFileAdminForm, MultimediaFileAdminForm, OSMForm
from chimere.models import Category, Icon, SubCategory, Marker, \
     PropertyModel, News, Route, Area, ColorTheme, Color, \
     MultimediaFile, PictureFile, Importer, Layer, AreaLayers,\
     get_areas_for_user, get_users_by_area
from chimere.utils import unicode_normalize, ShapefileManager, KMLManager,\
                          CSVManager
from chimere.widgets import TextareaWidget

def disable(modeladmin, request, queryset):
    for item in queryset:
        item.status = 'D'
        item.save()
disable.short_description = _(u"Disable")

def validate(modeladmin, request, queryset):
    for item in queryset:
        item.status = 'A'
        item.save()
validate.short_description = _(u"Validate")

def export_to_kml(modeladmin, request, queryset):
    u"""
    Export data to KML
    """
    filename, result = KMLManager.export(queryset)
    response = HttpResponse(result,
                        mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
export_to_kml.short_description = _(u"Export to KML")

def export_to_shapefile(modeladmin, request, queryset):
    u"""
    Export data to Shapefile
    """
    filename, zip_stream = ShapefileManager.export(queryset)
    # Stick it all in a django HttpResponse
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % filename
    response['Content-length'] = str(len(zip_stream))
    response['Content-Type'] = 'application/zip'
    response.write(zip_stream)
    return response
export_to_shapefile.short_description = _(u"Export to Shapefile")

def export_to_csv(modeladmin, request, queryset):
    u"""
    Export data to CSV
    """
    filename, result = CSVManager.export(queryset)
    response = HttpResponse(result, mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
export_to_csv.short_description = _(u"Export to CSV")

def managed_modified(modeladmin, request, queryset):
    # not very clean... There is must be a better way to do that
    redirect_url = request.get_full_path().split('admin_modification')[0]
    if queryset.count() != 1:
        messages.error(request, _(u"Only one item can be managed at a "
                                  u"time."))
        return HttpResponseRedirect(redirect_url)

    item = queryset.all()[0]
    if not item.ref_item or item.ref_item == item:
        try:
            item = modeladmin.model.objects.get(ref_item=item)
        except ObjectDoesNotExist:
            messages.error(request, _(u"No modified item associated "
                                      u"to the selected item."))
            return HttpResponseRedirect(redirect_url)
    item_ref = item.ref_item
    if request.POST.get('rapprochement'):
        couple = [(item, item_ref)]
        if hasattr(item, 'associated_marker'):
            couple.append((item.associated_marker.all()[0],
                           item_ref.associated_marker.all()[0]))
        updated = dict(request.POST)
        # clean
        for k in ('action', 'rapprochement', 'index', '_selected_action'):
            if k in updated:
                updated.pop(k)
        for idx, cpl in enumerate(couple):
            it, it_ref = cpl
            # don't copy geometry of associated items
            if idx:
                for k in ('route', 'point'):
                    if k in updated:
                        updated.pop(k)
            updated_keys = updated.keys()
            if it.status == 'I':
                updated_keys.append('import_version')
            for k in updated_keys:
                if k != 'import_version' and not request.POST[k]:
                    continue
                if hasattr(it_ref, k):
                    c_value = getattr(it_ref, k)
                    if hasattr(c_value, 'select_related'):
                        c_value.clear()
                        for val in getattr(it, k).all():
                            c_value.add(val)
                    else:
                        setattr(it_ref, k, getattr(it, k))
                        it_ref.save()
                elif k.startswith('property_'):
                    try:
                        pm = PropertyModel.get(pk=int(k[len('property_'):]))
                        it_ref.setProperty(pm, it.getProperty(pm))
                    except (ValueError, ObjectDoesNotExist):
                        pass
        if hasattr(item, 'associated_marker'):
            for it in item.associated_marker.all():
                it.delete()
        item.delete()
        messages.success(request, _(u"Modified item traited."))
        return HttpResponseRedirect(redirect_url)
    return render_to_response('admin/chimere/managed_modified.html',
                              {'item':item, 'item_ref':item_ref},
                              context_instance=RequestContext(request))
managed_modified.short_description = _(u"Managed modified items")

class PictureInline(admin.TabularInline):
    model = PictureFile
    extra = 1
    ordering = ('order',)
    form = PictureFileAdminForm
    readonly_fields = ('height', 'width')
    exclude = ('thumbnailfile', 'thumbnailfile_height', 'thumbnailfile_width')

class MultimediaInline(admin.TabularInline):
    model = MultimediaFile
    extra = 1
    ordering = ('order',)
    form = MultimediaFileAdminForm

class MarkerAdmin(admin.ModelAdmin):
    """
    Specialized the Point field.
    """
    search_fields = ("name",)
    list_display = ('name', 'status')
    list_filter = ('status', 'categories')
    actions = [validate, disable, managed_modified, export_to_kml,
               export_to_shapefile, export_to_csv]
    exclude = ['submiter_session_key', 'import_key', 'import_version',
               'available_date']
    readonly_fields = ['submiter_email', 'submiter_comment', 'import_source',
                       'ref_item', 'modified_since_import', 'route']
    form = MarkerAdminForm
    fieldsets = ((None, {
                    'fields': ['point', 'name', 'status', 'categories',
                               'description', 'start_date', 'end_date']
                  }),
                 (_(u"Submitter"), {
                    'classes':('collapse',),
                    'fields': ('submiter_name', 'submiter_email',
                               'submiter_comment')
                 }),
                 (_(u"Import"), {
                    'classes':('collapse',),
                    'fields': ('not_for_osm', 'modified_since_import',
                               'import_source', 'origin', 'license')
                 }),
                 (_(u"Associated items"), {
                    'classes':('collapse',),
                    'fields': ('ref_item', 'route',)
                 }),
                )
    inlines = [MultimediaInline, PictureInline]

    def __init__(self, *args, **kwargs):
        """
        Manage properties in fieldsets.
        """
        main_fields = self.fieldsets[0][1]['fields']
        for pm in PropertyModel.objects.filter(available=True).order_by('order'
                                               ).all():
            pm_name = pm.getNamedId()
            if pm_name not in main_fields:
                main_fields.append(pm_name)
        super(MarkerAdmin, self).__init__(*args, **kwargs)

    def queryset(self, request):
        qs = self.model._default_manager.get_query_set()
        if not request.user.is_superuser:
            areas = get_areas_for_user(request.user)
            contained = Q()
            for area in areas:
                contained = contained | area.getIncludeMarker()
            qs = qs.filter(contained)
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs.distinct()

    def admin_modification(self, request, item_id):
        '''
        Redirect to the marker modification form
        '''
        return managed_modified(self, request,
                            Marker.objects.filter(pk=item_id))
    def get_urls(self):
        from django.conf.urls.defaults import *
        urls = super(MarkerAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^admin_modification/(?P<item_id>\d+)/$',
                self.admin_site.admin_view(self.admin_modification),
                name='admin-modification'),
        )
        return my_urls + urls


class RouteAdmin(MarkerAdmin):
    """
    Specialized the Route field.
    """
    search_fields = ("name",)
    list_display = ('name', 'status')
    list_filter = ('status', 'categories')
    exclude = ['height', 'width']
    form = RouteAdminForm
    readonly_fields = ('associated_file', 'ref_item', 'has_associated_marker')
    actions = [validate, disable, managed_modified, export_to_kml,
               export_to_shapefile, export_to_csv]
    fieldsets = ((None, {
                    'fields': ['route', 'name', 'status', 'categories',
                               'start_date', 'end_date']
                  }),
                 (_(u"Submitter"), {
                    'classes':('collapse',),
                    'fields': ('submiter_name', 'submiter_email',
                               'submiter_comment')
                 }),
                 (_(u"Import"), {
                    'classes':('collapse',),
                    'fields': ('modified_since_import', 'import_source',
                               'origin', 'license')
                 }),
                 (_(u"Associated items"), {
                    'classes':('collapse',),
                    'fields': ('ref_item', 'associated_file',
                               'has_associated_marker')
                 }),
                )
    inlines = []

    def queryset(self, request):
        qs = self.model._default_manager.get_query_set()
        if not request.user.is_superuser:
            areas = get_areas_for_user(request.user)
            contained = Q()
            for area in areas:
                contained = contained | area.getIncludeRoute()
            qs = qs.filter(contained)
        ordering = self.ordering or ()
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def admin_modification(self, request, item_id):
        '''
        Redirect to the route modification form
        '''
        return managed_modified(self, request,
                                Route.objects.filter(pk=item_id))

class LayerInline(admin.TabularInline):
    model = AreaLayers
    extra = 1

class AreaAdmin(admin.ModelAdmin):
    """
    Specialized the area field.
    """
    form = AreaAdminForm
    exclude = ['upper_left_corner', 'lower_right_corner']
    inlines = [LayerInline]
    list_display = ['name', 'order', 'available', 'default']

def importing(modeladmin, request, queryset):
    for importer in queryset:
        importer.state = unicode(tasks.IMPORT_MESSAGES['import_pending'][0])
        importer.save()
        tasks.importing(importer.pk)
importing.short_description = _(u"Import")

def cancel_import(modeladmin, request, queryset):
    for importer in queryset:
        importer.state = tasks.IMPORT_MESSAGES['import_cancel'][0]
        importer.save()
cancel_import.short_description = _(u"Cancel import")

def cancel_export(modeladmin, request, queryset):
    for importer in queryset:
        importer.state = tasks.IMPORT_MESSAGES['export_cancel'][0]
        importer.save()
cancel_export.short_description = _(u"Cancel export")

def export_to_osm(modeladmin, request, queryset):
    if queryset.count() > 1:
        messages.error(request, _(u"Can manage only one OSM export at a time."))
        return HttpResponseRedirect(request.get_full_path())
    importer = queryset.all()[0]
    if Marker.objects.filter(categories__in=importer.categories.all(),
                             status='I').count():
        messages.error(request, _(u"You must treat all item with the status "\
                                  u"\"imported\" before exporting to OSM."))
        return HttpResponseRedirect(request.get_full_path())
    if importer.importer_type != 'OSM':
        messages.error(request, _(u"Only OSM importer are managed for export."))
        return HttpResponseRedirect(request.get_full_path())
    item_nb = Marker.objects.filter(status='A',
                categories=importer.categories.all(),
                not_for_osm=False, modified_since_import=True,
                route=None).count()
    if not item_nb:
        messages.error(request, _(u"No point of interest are concerned by this "
                                  u"export."))
        return HttpResponseRedirect(request.get_full_path())
    form = None
    if request.method == 'POST' and (
      'email' in request.POST or 'api' in request.POST
      or 'password' in request.POST):
        form = OSMForm(request.POST)
        if form.is_valid():
            importer.state = unicode(tasks.IMPORT_MESSAGES['export_pending'][0])
            importer.save()
            tasks.exporting(importer.pk, form.cleaned_data)
            messages.success(request, _(u"Export launched."))
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = OSMForm()
    msg_item = _(u"%s point(s) of interest concerned by this export before "\
                 u"bounding box filter.") % item_nb
    return render_to_response('admin/chimere/osm_export.html', {'item':importer,
                                             'form':form, 'msg_item':msg_item},
                              context_instance=RequestContext(request))
export_to_osm.short_description = _(u"Export to osm")

class ImporterAdmin(admin.ModelAdmin):
    form = ImporterAdminForm
    list_display = ('display_categories', 'default_name', 'importer_type',
                    'source', 'state', 'filtr')
    list_filter = ('importer_type',)
    readonly_fields = ('state',)
    actions = [importing, cancel_import, export_to_osm, cancel_export]
admin.site.register(Importer, ImporterAdmin)

class PropertyModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'available')

class NewsAdmin(admin.ModelAdmin):
    """
    Use the TinyMCE widget for the news content
    """
    form = NewsAdminForm

class SubcatInline(admin.TabularInline):
    model = SubCategory
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    """
    Use the TinyMCE widget for categories
    """
    form = CategoryAdminForm
    inlines = [SubcatInline]
    list_display = ['name', 'order']

class ColorInline(admin.TabularInline):
    model = Color

class ColorThemeAdmin(admin.ModelAdmin):
    inlines = [ColorInline,]

class IconAdmin(admin.ModelAdmin):
    exclude = ['height', 'width']

# register of differents database fields
admin.site.register(News, NewsAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Icon, IconAdmin)
admin.site.register(Marker, MarkerAdmin)
admin.site.register(Route, RouteAdmin)
if not settings.CHIMERE_HIDE_PROPERTYMODEL:
    admin.site.register(PropertyModel, PropertyModelAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(ColorTheme, ColorThemeAdmin)
admin.site.register(Layer)
