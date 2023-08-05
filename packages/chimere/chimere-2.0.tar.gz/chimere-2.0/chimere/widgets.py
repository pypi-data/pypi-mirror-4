#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008-2012 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
Extra widgets and fields
"""
from django import conf
from django import forms
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

import re

def getMapJS(area_name=''):
    '''Variable initialization for drawing the map
    '''
    # projection, center and bounds definitions
    js = u"var epsg_display_projection = new OpenLayers.Projection('EPSG:%d')"\
         u";\n" % settings.CHIMERE_EPSG_DISPLAY_PROJECTION
    js += u"OpenLayers.ImgPath = '%schimere/img/';\n" % settings.STATIC_URL
    js += u"var epsg_projection = new OpenLayers.Projection('EPSG:%d');\n" % \
                                               settings.CHIMERE_EPSG_PROJECTION
    js += u"var centerLonLat = new OpenLayers.LonLat(%f,"\
          u"%f).transform(epsg_display_projection, epsg_projection);\n" % \
                                               settings.CHIMERE_DEFAULT_CENTER
    js += u"var media_path = '%s';\n" % settings.MEDIA_URL
    js += u"var static_path = '%s';\n" % settings.STATIC_URL
    js += u"var map_layer = %s;\n" % settings.CHIMERE_DEFAULT_MAP_LAYER
    js += u"var restricted_extent;\n"

    if area_name:
        js += u"var area_name='%s';\n" % area_name
    js = u"<script type='text/javascript'><!--\n"\
         u"%s// !--></script>\n" % js
    return js

def get_map_layers(area_name=''):
    from chimere.models import Area
    area = None
    if area_name:
        try:
            area = Area.objects.get(urn=area_name)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            area = Area.objects.get(default=True)
        except ObjectDoesNotExist:
            pass
    map_layers, default = [], None
    if area and area.layers.count():
        map_layers = [layer.layer_code
                for layer in area.layers.order_by('arealayers__order').all()]
        def_layer = area.layers.filter(arealayers__default=True)
        if def_layer.count():
            def_layer = def_layer.all()[0]
            for order, map_layer in enumerate(map_layers):
                if map_layer == def_layer.layer_code:
                    default = order
    elif settings.CHIMERE_DEFAULT_MAP_LAYER:
        map_layers = [settings.CHIMERE_DEFAULT_MAP_LAYER]
    else:
        map_layers = ["new OpenLayers.Layer.OSM.Mapnik('Mapnik')"]
    return map_layers, default

class ChosenSelectWidget(forms.Select):
    """
    Chosen select widget.
    """
    class Media:
        js = ["%schosen/chosen/chosen.jquery.min.js" % settings.STATIC_URL,]
        css = {'all':
             ["%schosen/chosen/chosen.css" % settings.STATIC_URL,]
              }
    def render(self, *args, **kwargs):
        if 'attrs' not in kwargs:
            kwargs['attrs'] = {}
        kwargs['attrs'].update({'class': 'chzn-select'})
        rendered = super(ChosenSelectWidget, self).render(*args, **kwargs)
        rendered += u"\n<script type='text/javascript'>\n"\
        u"  $('#%s').chosen();\n"\
        u"</script>\n" % kwargs['attrs']['id']
        return mark_safe(rendered)

class ImporterChoicesWidget(forms.Select):
    '''
    Importer select widget.
    '''
    class Media:
        js = ["%schimere/js/importer_interface.js" % settings.STATIC_URL,]

class TextareaWidgetBase(forms.Textarea):
    """
    Manage the edition of a text using TinyMCE
    """
    def render(self, *args, **kwargs):
        if 'attrs' not in kwargs:
            kwargs['attrs'] = {}
        if 'class' not in kwargs['attrs']:
            kwargs['attrs']['class'] = ''
        else:
            kwargs['attrs']['class'] += ' '
        kwargs['attrs']['class'] += 'mceEditor'
        rendered = super(TextareaWidgetBase, self).render(*args, **kwargs)
        return mark_safe(rendered)

class TextareaWidget(TextareaWidgetBase):
    """
    Manage the edition of a text using TinyMCE
    """
    class Media:
        js = ["%stiny_mce.js" % settings.TINYMCE_URL,
              "%schimere/js/textareas.js" % settings.STATIC_URL,]

class TextareaAdminWidget(TextareaWidgetBase):
    class Media:
        js = ["%stiny_mce.js" % settings.TINYMCE_URL,
              "%schimere/js/textareas_admin.js" % settings.STATIC_URL,]

class DatePickerWidget(forms.TextInput):
    """
    Manage the edition of dates.
    JQuery and Jquery-UI are already loaded by default so don't include
    them in Media files.
    """
    def render(self, *args, **kwargs):
        rendered = super(DatePickerWidget, self).render(*args, **kwargs)
        rendered += u"\n<script type='text/javascript'>\n"\
        u"  $(function() {$('#%s').datepicker({ dateFormat: 'yy-mm-dd' });});\n"\
        u"</script>\n" % kwargs['attrs']['id']
        return mark_safe(rendered)

class PointChooserWidget(forms.TextInput):
    """
    Manage the edition of point on a map
    """
    class Media:
        css = {
            "all": settings.OSM_CSS_URLS + \
                   ["%schimere/css/forms.css" % settings.STATIC_URL,]
        }
        js = settings.OSM_JS_URLS + list(settings.JQUERY_JS_URLS) + \
             ["%schimere/js/jquery.chimere.js" % settings.STATIC_URL]

    def render(self, name, value, attrs=None, area_name=''):
        '''
        Render a map and latitude, longitude information field
        '''
        val = '0'
        value_x, value_y = 0, 0
        if value:
            val = str(value)
            if hasattr(value, 'x') and hasattr(value, 'y'):
                value_x, value_y = value.x, value.y
            elif isinstance(value, unicode) and value.startswith('POINT('):
                try:
                    value_x, value_y = value.split('(')[1][:-1].split(' ')
                    value_x, value_y = float(value_x), float(value_y)
                except:
                    value = None
            else:
                value = None
        map_layers, default_area = get_map_layers(area_name)
        js = """
        OpenLayers.ImgPath = '%schimere/img/';
        var EPSG_DISPLAY_PROJECTION = epsg_display_projection = new OpenLayers.Projection('EPSG:%s');
        var EPSG_PROJECTION = epsg_projection = new OpenLayers.Projection('EPSG:%s');
        var CENTER_LONLAT = centerLonLat = new OpenLayers.LonLat%s.transform(epsg_display_projection, epsg_projection);
        var DEFAULT_ZOOM = %s;
        var chimere_init_options = {};
        chimere_init_options["default_icon"] = new OpenLayers.Icon('%schimere/img/marker-green.png', new OpenLayers.Size(21, 25), new OpenLayers.Pixel(-(21/2), -25));
        chimere_init_options["map_layers"] = [%s];
        chimere_init_options['dynamic_categories'] = false;
        chimere_init_options['edition'] = true;
        chimere_init_options["checked_categories"] = [];
        """ % (settings.STATIC_URL, settings.CHIMERE_EPSG_DISPLAY_PROJECTION,
              settings.CHIMERE_EPSG_PROJECTION, settings.CHIMERE_DEFAULT_CENTER,
              settings.CHIMERE_DEFAULT_ZOOM, settings.STATIC_URL,
              ", ".join(map_layers))
        if default_area:
            js += "chimere_init_options['selected_map_layer'] = %d;\n" % \
                  default_area
        #TODO: manage area
        tpl = u"<script type='text/javascript'><!--\n"\
              u"%s// !--></script>\n" % js
        tpl += u"</div><div id='map_edit'></div>"\
               u"<div id='live_lonlat'>"\
               u"    <p><label for='live_latitude'>%s</label>"\
               u" <input type='texte' name='live_latitude' id='live_latitude' "\
               u"size='8' disabled='true' value='%f'/></p>"\
               u"<p><label for='live_longitude'>%s</label><input type='texte' "\
               u"name='live_longitude' id='live_longitude' size='8' "\
               u"disabled='true' value='%f'/></p>"\
               u"<input type='hidden' name='%s' id='id_%s' value='%s'/>" % (
                    _("Latitude"), value_y, _("Longitude"), value_x, name, name,
                    val)
        tpl += "<script type='text/javascript'><!--\n"
        tpl += "$('#map_edit').chimere(chimere_init_options);\n"
        if value:
            tpl += u'var mylonlat = new OpenLayers.LonLat(%f,%f);\n'\
                   u'$("#map_edit").chimere("putEditMarker", \n'\
                   u'   mylonlat.transform(EPSG_DISPLAY_PROJECTION, \n'\
                   u'                      EPSG_PROJECTION), true);\n' % (
                                                             value_x, value_y)
        tpl += "// --></script>\n"
        return mark_safe(tpl)

class PointField(models.PointField):
    '''
    Set the widget for the form field
    '''
    def formfield(self, **keys):
        defaults = {'widget': PointChooserWidget}
        keys.update(defaults)
        return super(PointField, self).formfield(**keys)

    def clean(self, value, instance=None):
        if len(value) != 2 and self.required:
            raise ValidationError(_("Invalid point"))
        return value

class RouteChooserWidget(forms.TextInput):
    """
    Manage the edition of route on a map
    """
    class Media:
        css = {"all": settings.OSM_CSS_URLS + \
                      ["%schimere/css/forms.css" % settings.STATIC_URL,]
        }
        js = settings.OSM_JS_URLS + list(settings.JQUERY_JS_URLS) + \
             ["%schimere/js/jquery.chimere.js" % settings.STATIC_URL,
              "%schimere/js/edit_route_map.js" % settings.STATIC_URL,
              "%schimere/js/base.js" % settings.STATIC_URL,]

    def render(self, name, value, attrs=None, area_name='', routefile_id=None):
        '''
        Render a map and latitude, longitude information field
        '''
        tpl = getMapJS(area_name)
        map_layers, default_area = get_map_layers(area_name)
        js = """
        var extra_url = "%s";
        OpenLayers.ImgPath = '%schimere/img/';
        var EPSG_DISPLAY_PROJECTION = epsg_display_projection = new OpenLayers.Projection('EPSG:%s');
        var EPSG_PROJECTION = epsg_projection = new OpenLayers.Projection('EPSG:%s');
        var CENTER_LONLAT = centerLonLat = new OpenLayers.LonLat%s.transform(epsg_display_projection, epsg_projection);
        var DEFAULT_ZOOM = %s;
        var chimere_init_options = {};
        chimere_init_options["map_layers"] = [%s];
        chimere_init_options['dynamic_categories'] = false;
        chimere_init_options['edition'] = true;
        chimere_init_options['edition_type_is_route'] = true;
        chimere_init_options["checked_categories"] = [];
        """ % ( reverse("chimere:index"), settings.STATIC_URL,
              settings.CHIMERE_EPSG_DISPLAY_PROJECTION,
              settings.CHIMERE_EPSG_PROJECTION, settings.CHIMERE_DEFAULT_CENTER,
              settings.CHIMERE_DEFAULT_ZOOM, ", ".join(map_layers))
        if default_area:
            js += "chimere_init_options['selected_map_layer'] = %d;\n" % \
                  default_area
        tpl = u"<script type='text/javascript'><!--\n"\
              u"%s// !--></script>\n" % js
        #TODO: manage area
        help_create = ''
        if not value:
            help_create = u"<h3>%s</h3>\n"\
            u"<p>%s</p>\n"\
            u"<p>%s</p>\n"\
            u"<p>%s</p>\n"\
            u"<p>%s</p>\n"\
            u"<p>%s</p>\n" % (_(u"Creation mode"),
            _(u"To start drawing the route click on the toggle button: "\
              u"\"Draw\"."),
            _(u"Then click on the map to begin the drawing."),
            _(u"You can add points by clicking again."),
            _(u"To finish the drawing double click. When the drawing is "\
              u"finished you can edit it."),
            _(u"While creating to undo a drawing click again on the toggle "\
              u"button \"Stop drawing\"."))
        help_modify = u"<h3>%s</h3>\n"\
        u"<p>%s</p>\n"\
        u"<p>%s</p>\n"\
        u"<p>%s</p>\n" % (_(u"Modification mode"),
        _(u"To move a point click on it and drag it to the desired position."),
        _(u"To delete a point move the mouse cursor over it and press the "\
          u"\"d\" or \"Del\" key."),
        _(u"To add a point click in the middle of a segment and drag the new "\
          u"point to the desired position"))
        if not value:
            # upload a file
            tpl += u"<script type='text/javascript'><!--\n"\
                   u"    var error_msg = \"%s\";"\
                   u"// --></script>" % (
                   _(u"Give a name and set category before uploading a file."))
            tpl += u'<div id="upload"><a href="#" class="upload-button" '\
               u'onclick="uploadFile(error_msg);return false;">%s</a></div>' % (
                    _(u"Upload a route file (GPX or KML)"))
            tpl += u"\n<p id='draw-or'>%s</p>\n" % _(u"or")
            tpl += u"<div id='draw-label'><div id='draw-toggle-off' "\
                   u"onclick='toggleDraw();'>\n"\
                   u"<a href='#' onclick='return false;'>%s</a></div>"\
                   u"</div>\n"\
                   u"<hr class='spacer'/>" % (_(u"Start \"hand\" drawing"))
        style = ''
        if value:
            style = " style='display:block'"
        tpl += u"\n<div class='help-route' id='help-route-modify'%s>%s</div>"\
        u"\n<hr class='spacer'/>\n"\
        u"<input type='hidden' name='%s' id='id_%s' value=\"%s\"/>\n"\
        u"<input type='hidden' name='associated_file_id' "\
        u"id='id_associated_file_id' value=\"%s\"/>\n" % (
            style, help_modify, name, name, value, routefile_id)
        if value:
            tpl += u"\n<div id='map_edit'></div>"
        else:
            tpl += "\n<div class='help-route' id='help-route-create'>%s</div>"\
                   % help_create
            tpl += u"\n<div id='map_edit'>\n"\
                   u"  <div class='map_button'>\n"\
            u"  <a href='#' id='button-move-map' class='toggle-button "\
            u"toggle-button-active' onclick='toggleDrawOff();return false;'>%s"\
            u"</a>\n"\
            u"<a href='#' id='button-draw-map' class='toggle-button "\
            u"toggle-button-inactive' onclick='toggleDrawOn();return false;'>"\
            u"%s</a></div>\n"\
            u"  </div>" % (_(u"Move on the map"), _(u"Draw"))
        tpl += u"<script type='text/javascript'><!--\n"
        if not value:
            tpl += u"jQuery('#map_edit').hide();"
        if value:
            tpl += u"jQuery('#map_edit').chimere(chimere_init_options);\n"
            val = value
            if type(value) == unicode:
                try:
                    val = fromstr(value)
                except:
                    pass
            if hasattr(val, 'json'):
                tpl += u"\nvar geometry='%s';\n"\
                       u"jQuery('#map_edit').chimere('initFeature', geometry);"\
                       % val.json
        tpl += u"\n// --></script>\n"
        return mark_safe(tpl)

class RouteField(models.LineStringField):
    '''
    Set the widget for the form field
    '''
    def formfield(self, **keys):
        defaults = {'widget': RouteChooserWidget}
        keys.update(defaults)
        return super(RouteField, self).formfield(**keys)

class AreaWidget(forms.TextInput):
    """
    Manage the edition of an area on the map
    """
    class Media:
        css = {
            "all": settings.OSM_CSS_URLS + \
                   ["%schimere/css/forms.css" % settings.STATIC_URL,]
        }
        js = settings.OSM_JS_URLS + [
              "%schimere/js/edit_area.js" % settings.STATIC_URL,
              "%schimere/js/base.js" % settings.STATIC_URL,]

    def get_bounding_box_from_value(self, value):
        '''
        Return upper left lat/lon and lower lat/lon from the input value
        '''
        upper_left_lat, upper_left_lon = 0, 0
        lower_right_lat, lower_right_lon = 0, 0
        if not value:
            return upper_left_lat, upper_left_lon, lower_right_lat, \
                   lower_right_lon
        if len(value) == 2:
            upper_left = value[0]
            lower_right = value[1]
            if hasattr(upper_left, 'x') and hasattr(upper_left, 'y'):
                upper_left_lon, upper_left_lat = upper_left.x, upper_left.y
            elif len(upper_left) == 2:
                try:
                    upper_left_lon = float(upper_left[0])
                    upper_left_lat = float(upper_left[1])
                except ValueError:
                    pass
            if hasattr(lower_right, 'x') and hasattr(lower_right, 'y'):
                lower_right_lon, lower_right_lat = lower_right.x, \
                                                   lower_right.y
            elif len(lower_right) == 2:
                lower_right_lon, lower_right_lat = lower_right
                try:
                    lower_right_lon = float(lower_right[0])
                    lower_right_lat = float(lower_right[1])
                except ValueError:
                    pass
        return upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon

    def render(self, name, value, attrs=None, initialized=True):
        """
        Render a map
        """
        upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon = \
                                        self.get_bounding_box_from_value(value)
        tpl = getMapJS()
        tpl += u"</div>\n"\
        u"<input type='hidden' name='upper_left_lat' id='upper_left_lat' "\
        u"value='%f'/>\n"\
        u"<input type='hidden' name='upper_left_lon' id='upper_left_lon' "\
        u"value='%f'/>\n"\
        u"<input type='hidden' name='lower_right_lat' id='lower_right_lat' "\
        u"value='%f'/>\n"\
        u"<input type='hidden' name='lower_right_lon' id='lower_right_lon' "\
        u"value='%f'/>\n" % (
            upper_left_lat, upper_left_lon, lower_right_lat, lower_right_lon)
        help_msg = _(u"Hold CTRL, click and drag to select area on the map")
        tpl += u"<p class='help-osm'>%s</p>\n" % help_msg
        tpl += u"<script type='text/javascript'>\n"
        tpl += u"function init_map_form (){\ninit();\n"
        if value:
            tpl += u"var extent = new OpenLayers.Bounds(%f, %f, %f, %f);\n"\
            u"extent.transform(epsg_display_projection, epsg_projection);\n"\
            u"updateForm(extent);\n"\
            u"map.zoomToExtent(extent, true);\n"\
            u"map.zoomOut();" % (upper_left_lon, upper_left_lat,
                                 lower_right_lon, lower_right_lat)
        tpl += u"}\n"
        if initialized:
            tpl += u"$(document).ready(function($) {init_map_form()});\n"
        tpl += u"</script>\n"
        tpl += u"<div id='map_edit'>\n"
        return mark_safe(tpl)

    def value_from_datadict(self, data, files, name):
        """
        Return the appropriate values
        """
        values = []
        for keys in (('upper_left_lon', 'upper_left_lat',),
                     ('lower_right_lon', 'lower_right_lat')):
            value = []
            for key in keys:
                val = data.get(key, None)
                if not val:
                    return []
                value.append(val)
            values.append(value)
        return values

RE_XAPI = re.compile('(node|way)\[(.*=.*)\]\[bbox='\
          '(-*[0-9]*.[0-9]*,-*[0-9]*.[0-9]*,-*[0-9]*.[0-9]*,-*[0-9]*.[0-9]*)\]')

class ImportFiltrWidget(AreaWidget):
    """
    Manage the edition of the import source field
    """
    class Media:
        css = {
            "all": settings.OSM_CSS_URLS + \
                   ["%schimere/css/forms.css" % settings.STATIC_URL,]
        }
        js = settings.OSM_JS_URLS + [
              "%schimere/js/edit_area.js" % settings.STATIC_URL,
              "%schimere/js/base.js" % settings.STATIC_URL,]

    def render(self, name, value, attrs=None):
        """
        Render a map
        """
        tpl = super(ImportFiltrWidget, self).render(name, value, attrs,
                                                     initialized=False)
        tpl += u"</div><hr class='spacer'/>"
        vals = {'lbl':_(u"Type:"), 'name':name, 'node':_(u"Node"),
                'way':_(u"Way")}
        vals['way_selected'] = ' checked="checked"'\
                               if self.xapi_type == 'way' else ''
        vals['node_selected'] = ' checked="checked"'\
                               if self.xapi_type == 'node' else ''
        tpl += u"<div class='input-osm'><label>%(lbl)s</label>"\
         u"<input type='radio' name='id_%(name)s_type' id='id_%(name)s_node'"\
         u" value='node'%(node_selected)s/> <label for='id_%(name)s_node'>"\
         u"%(node)s</label> <input type='radio' name='id_%(name)s_type' "\
         u"id='id_%(name)s_way' value='way'%(way_selected)s/> <label "\
         u"for='id_%(name)s_way'>%(way)s</label></div>" % vals
        help_msg = _(u"Enter an OSM \"tag=value\" string such as "\
             u"\"amenity=pub\". A list of common tag is available "\
             u"<a href='https://wiki.openstreetmap.org/wiki/Map_Features' "\
             u" target='_blank'>here</a>.")
        tpl += u"<p class='help-osm'>%s</p>\n" % help_msg
        tpl += u"<div class='input-osm'><label for='id_%s_tag'>%s</label>"\
               u"<input type='text' id='id_%s_tag' value=\"%s\"/></div>" % (
                                         name, _(u"Tag:"), name, self.xapi_tag)
        tpl += u"<script type='text/javascript'>\n"
        tpl += u"var default_xapi='%s';" % settings.CHIMERE_XAPI_URL
        tpl += u'var msg_missing_area = "%s";' % \
                                            _(u"You have to select an area.")
        tpl += u'var msg_missing_type = "%s";' % \
                                            _(u"You have to select a type.")
        tpl += u'var msg_missing_filtr = "%s";' % \
                                         _(u"You have to insert a filter tag.")
        tpl += u"</script>\n"
        help_msg = _(u"If you change the above form don't forget to refresh "\
                     u"before submit!")
        tpl += u"<p class='help-osm errornote'>%s</p>\n" % help_msg
        help_msg = _(u"You can put a Folder name of the KML file to filter on "\
                     u"it.")
        tpl += u"<p class='help-kml'>%s</p>\n" % help_msg
        if not value:
            value = ''
        tpl += u"<div><input type='text' id='id_%s' name='id_%s' "\
               u"value=\"%s\"/> <input type='button' id='id_refresh_%s' "\
               u"value='%s' class='input-osm'/>" % (name, name, value, name,
                                                    _(u"Refresh"))
        return mark_safe(tpl)

    def value_from_datadict(self, data, files, name):
        """
        Return the appropriate values
        """
        return data.get('id_'+name, None)

    def get_bounding_box_from_value(self, value):
        '''
        Return upper left lat/lon, lower lat/lon from the input value.
        Get also xapi type and xapi tag
        '''
        upper_left_lat, upper_left_lon = 0, 0
        lower_right_lat, lower_right_lon = 0, 0
        self.xapi_type, self.xapi_tag, self.bounding_box = None, '', None
        if not value:
            return upper_left_lat, upper_left_lon, lower_right_lat, \
                   lower_right_lon
        xapi_m = RE_XAPI.match(value)
        if not xapi_m:
            return upper_left_lat, upper_left_lon, lower_right_lat, \
                   lower_right_lon
        # as the regexp pass, we could be pretty confident
        self.xapi_type, self.xapi_tag, self.bounding_box = xapi_m.groups()
        upper_left_lon, lower_right_lat, lower_right_lon, upper_left_lat = \
                self.bounding_box.split(',')
        return float(upper_left_lat), float(upper_left_lon), \
               float(lower_right_lat), float(lower_right_lon)

class AreaField(forms.MultiValueField):
    '''
    Set the widget for the form field
    '''
    widget = AreaWidget

    def compress(self, data_list):
        if not data_list:
            return None
        return data_list

class MultiSelectWidget(forms.SelectMultiple):
    class Media:
        css = {'all': list(settings.JQUERY_CSS_URLS) + [
            settings.STATIC_URL + 'chimere/js/jquery/bsmSelect/css/jquery.bsmselect.css',
            settings.STATIC_URL + 'chimere/js/jquery/bsmSelect/css/jquery.bsmselect.custom.css',
            ]
        }
        js = list(settings.JQUERY_JS_URLS) + [
            settings.STATIC_URL + 'chimere/js/jquery/bsmSelect/js/jquery.bsmselect.js',
            settings.STATIC_URL + 'chimere/js/jquery/bsmSelect/js/jquery.bsmselect.compatibility.js',
            ]

    def render(self, name, value, attrs=None):
        rendered = super(MultiSelectWidget, self).render(name, value, attrs)
        rendered += u"<hr class='spacer'/><script type='text/javascript'>\n"\
        u"$.bsmSelect.conf['title'] = \"%(title)s\";\n"\
        u"$(\"#id_%(name)s\").bsmSelect({\n"\
        u"    removeLabel: '<strong>X</strong>',\n"\
        u"    containerClass: 'bsmContainer',\n"\
        u"    listClass: 'bsmList-custom',\n"\
        u"    listItemClass: 'bsmListItem-custom',\n"\
        u"    listItemLabelClass: 'bsmListItemLabel-custom',\n"\
        u"    removeClass: 'bsmListItemRemove-custom'\n"\
        u"});\n"\
        u"</script>\n" % {'name':name, 'title':_("Select...")}
        return mark_safe(rendered)

class SelectMultipleField(models.ManyToManyField):
    '''
    Set the widget for the category field
    '''
    def formfield(self, **keys):
        self.help_text = ""
        defaults = {'widget': MultiSelectWidget}
        keys.update(defaults)
        return super(SelectMultipleField, self).formfield(**keys)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^chimere\.widgets\.PointField"])
add_introspection_rules([], ["^chimere\.widgets\.SelectMultipleField"])
add_introspection_rules([], ["^chimere\.widgets\.RouteField"])
