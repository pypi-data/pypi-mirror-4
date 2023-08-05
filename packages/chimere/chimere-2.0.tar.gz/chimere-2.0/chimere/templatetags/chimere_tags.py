#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta

from logging import getLogger

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.template.loader import render_to_string

from chimere.models import Marker, Area, News, SubCategory, MultimediaType
from chimere.widgets import get_map_layers

log = getLogger(__name__)

register = template.Library()

@register.inclusion_tag('chimere/blocks/areas.html', takes_context=True)
def display_areas(context):
    """
    Display available areas.
    """
    context_data = {"areas": Area.getAvailable(),
                    "base_url": reverse('chimere:index')
                    }
    if "area_name" in context:
        context_data['area_name'] = context["area_name"]
    return context_data

@register.inclusion_tag('chimere/blocks/submited.html', takes_context=True)
def submited(context):
    """
    Submited message.
    """
    return {"edit_url":reverse('chimere:edit'),
            "index_url":reverse('chimere:index')}

@register.inclusion_tag('chimere/blocks/welcome.html', takes_context=True)
def display_news(context, display=False):
    """
    Welcome message and active news.
    """
    area = None
    context_data = {'display':display}
    if "area_name" in context:
        try:
            area = Area.objects.get(urn=context["area_name"])
            context_data['area_name'] = context['area_name']
            context_data['welcome_message'] = area.welcome_message
        except ObjectDoesNotExist:
            pass
    # Retrieve news
    news = News.objects.filter(available=True)
    if area:
        news = news.filter(Q(areas__isnull=True)|Q(areas__in=[area.pk]))
    news = list(news.all())
    if settings.CHIMERE_DAYS_BEFORE_EVENT:
        # Retrieve active markers
        today = date.today()
        after = today + timedelta(settings.CHIMERE_DAYS_BEFORE_EVENT)
        q = Marker.objects.filter(status='A', start_date__lte=after
                     ).filter(Q(end_date__gte=today)|Q(end_date__isnull=True))
        if area:
            q = q.filter(area.getIncludeMarker())
        news += list(q)
    news.sort(key=lambda x:x.date, reverse=True)
    context_data['news_lst'] = news
    return context_data

@register.inclusion_tag('chimere/blocks/head_jquery.html', takes_context=True)
def head_jquery(context):
    """
    Create context and display head elements (js, css, etc.) for jquery.
    """
    context_data = {
            "JQUERY_JS_URLS": settings.JQUERY_JS_URLS,
            "JQUERY_CSS_URLS": settings.JQUERY_CSS_URLS,
             }
    return context_data

@register.inclusion_tag('chimere/blocks/head_jme.html', takes_context=True)
def head_jme(context):
    """
    Create context and display head elements (js, css, etc.) for jme.
    """
    context_data = {
            "STATIC_URL": settings.STATIC_URL,
             }
    return context_data

@register.inclusion_tag('chimere/blocks/head_chimere.html', takes_context=True)
def head_chimere(context):
    """
    Create context and display head elements (js, css, etc.) for chimere.
    """
    area_name = context['area_name'] if 'area_name' in context else 'area_name'
    area = None
    if area_name:
        try:
            area = Area.objects.get(urn=area_name)
        except ObjectDoesNotExist:
            pass
    context_data = {
            "STATIC_URL": settings.STATIC_URL,
            "MEDIA_URL": settings.MEDIA_URL,
            "DYNAMIC_CATEGORIES": 'true' if area and area.dynamic_categories \
                                  else 'false',
            "EXTRA_URL": reverse("chimere:index"),
            "EPSG_DISPLAY_PROJECTION": settings.CHIMERE_EPSG_DISPLAY_PROJECTION,
            "EPSG_PROJECTION": settings.CHIMERE_EPSG_PROJECTION,
            "DEFAULT_CENTER": settings.CHIMERE_DEFAULT_CENTER,
            "DEFAULT_ZOOM": settings.CHIMERE_DEFAULT_ZOOM,
            "MAP_LAYER": settings.CHIMERE_DEFAULT_MAP_LAYER,
            "OSM_CSS_URLS": settings.OSM_CSS_URLS,
            "OSM_JS_URLS": settings.OSM_JS_URLS,
             }
    return context_data

@register.inclusion_tag('chimere/blocks/map.html', takes_context=True)
def map(context, map_id='map'):
    context_data =  {'map_id':map_id,
                     "STATIC_URL": settings.STATIC_URL}
    context_data['icon_offset_x'] = settings.CHIMERE_ICON_OFFSET_X
    context_data['icon_offset_y'] = settings.CHIMERE_ICON_OFFSET_Y
    context_data['icon_width'] = settings.CHIMERE_ICON_WIDTH
    context_data['icon_height'] = settings.CHIMERE_ICON_HEIGHT
    area_name = context['area_name'] if 'area_name' in context else 'area_name'
    map_layers, default_area = get_map_layers(area_name)
    context_data['map_layers'] = ", ".join(map_layers)
    if default_area:
        context_data['selected_map_layer'] = default_area
    context_data['p_checked_categories'] = None
    area = None
    if area_name:
        try:
            area = Area.objects.get(urn=area_name)
        except ObjectDoesNotExist:
            pass
    if not area:
        try:
            area = Area.objects.get(default=True)
        except ObjectDoesNotExist:
            pass
    if area:
        context_data['area_id'] = area_name
        if 'zoomout' in context and context['zoomout']:
            context_data['zoom'] = "[%s]" % ",".join((
                unicode(area.upper_left_corner.x),
                unicode(area.upper_left_corner.y),
                unicode(area.lower_right_corner.x),
                unicode(area.lower_right_corner.y)))
        if area.subcategories.filter(available=True).count() == 1:
            context_data['single_category'] = True
            context_data['p_checked_categories'] = "[%d]" % \
                                            area.subcategories.all()[0].pk
        elif area.default_subcategories.count():
            context_data['p_checked_categories'] = unicode([subcategory.pk
                    for subcategory in area.default_subcategories.all()])
        if area.restrict_to_extent:
            context_data['restricted_extent'] = """
var bounds = new OpenLayers.Bounds();
bounds.extend(new OpenLayers.LonLat(%f, %f));
bounds.extend(new OpenLayers.LonLat(%f, %f));
""" % (area.upper_left_corner.x, area.upper_left_corner.y,
       area.lower_right_corner.x, area.lower_right_corner.y)

    if SubCategory.objects.filter(available=True).count() <= 1:
        context_data['single_category'] = True
        if not context_data['p_checked_categories']:
            cat = ''
            if SubCategory.objects.filter(available=True).count():
                cat = unicode(SubCategory.objects.filter(available=True
                                                         ).all()[0].pk)
            context_data['p_checked_categories'] = "[%s]" % cat
    if not context_data['p_checked_categories']:
        context_data['p_checked_categories'] = "[]"
    context_data['dynamic_categories'] = 'true' \
                            if area and area.dynamic_categories else 'false'
    if 'request' not in context:
        return context_data
    request = context['request']
    # Default values
    if request.GET:
        for key in ('zoom', 'lon', 'lat', 'display_submited',
                    'current_feature'):
            if key in request.GET and request.GET[key]:
                context_data['p_'+key] = request.GET[key]
            else:
                context_data['p_'+key] = None
        if 'checked_categories' in request.GET \
           and request.GET['checked_categories']:
            cats = request.GET['checked_categories'].split('_')
            context_data['p_checked_categories'] = "[%s]" % ",".join(cats)
    return context_data

@register.inclusion_tag('chimere/blocks/multimedia_file.html',
                        takes_context=True)
def multimedia_render(context, multimedia_file):
    context['multimedia_item'] = multimedia_file
    return context

@register.inclusion_tag('chimere/blocks/alternate_multimedia.html')
def alternate_multimedia(formset_multi, formset_picture):
    return {'formsets':[formset_multi, formset_picture],
            "STATIC_URL": settings.STATIC_URL,
            'auto_type_id':MultimediaType.objects.get(name='auto').pk}

@register.simple_tag
def get_tinyfied_url(marker, area_name=''):
    if not marker or not hasattr(marker, 'get_absolute_url'):
        return ""
    url = marker.get_absolute_url(area_name)
    return url

@register.filter(name='ol_map')
def ol_map(item, arg='map_id'):
    geom, geom_type = None, None
    if hasattr(item, 'point'):
        geom, geom_type = item.point, 'point'
    elif hasattr(item, 'route'):
        geom, geom_type = item.route, 'route'
    rendered = render_to_string('chimere/blocks/ol_map.html', {'geom': geom,
                                                               'map_id':arg})
    return rendered
