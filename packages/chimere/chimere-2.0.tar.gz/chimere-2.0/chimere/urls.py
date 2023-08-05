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

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

from chimere.models import Area
from chimere.feeds import LatestPOIsByCategory, LatestPOIsBySubCategory, \
                          LatestPOIs, LatestPOIsByZone, LatestPOIsByZoneID

def i18n_javascript(request):
    return admin.site.i18n_javascript(request)


urlpatterns = patterns('chimere.views',
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?simple$', 'index', {'simple':True},
        name="simple_index")
)

if settings.CHIMERE_FEEDS:
    urlpatterns += patterns('',
        url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?feeds$', 'chimere.views.rss',
            name='feeds-form'),
        url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?feeds/category/(?P<category_id>\d+)$',
            LatestPOIsByCategory(), name='feeds-cat'),
        url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?feeds/subcategory/(?P<category_id>\d+)$',
            LatestPOIsBySubCategory(), name='feeds-subcat'),
        url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?feeds/global/$', LatestPOIs(),
            name='feeds-global'),
        url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?feeds/area/(?P<area>[0-9-_.]+)$',
            LatestPOIsByZone(), name='feeds-area'),
        url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?feeds/areaid/(?P<area_id>\d+)$',
            LatestPOIsByZoneID(), name='feeds-areaid'),
    )

urlpatterns += patterns('chimere.views',
    url(r'^charte/?$', 'charte', name="charte"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?contact/?$', 'contactus', name="contact"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?edit/$', 'edit',
        name="edit"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?edit/(?P<item_id>\w+)/(?P<submited>\w+)?$',
            'edit', name="edit-item"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?edit-route/$', 'editRoute',
        name="editroute"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?edit-route/(?P<item_id>\w+)/(?P<submited>\w+)?$',
        'editRoute', name="editroute-item"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?getDetail/(?P<marker_id>\d+)/?$', 'getDetail',
        name="get_detail"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?getDescriptionDetail/?(?P<category_id>\d+)/?$',
                        'getDescriptionDetail', name="get_description_detail"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?getGeoObjects/'\
        r'(?P<category_ids>[a-zA-Z0-9_-]+)(/(?P<status>\w+))?$', 'getGeoObjects',
                        name="getgeoobjects"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?getAvailableCategories/$',
                        'get_available_categories', name="get_categories"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]*/)?ty/(?P<tiny_urn>\w+)$',
                        'redirectFromTinyURN', name="tiny"),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?upload_file/((?P<category_id>\w+)/)?$',
                        'uploadFile', name='upload_file'),
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+/)?process_route_file/(?P<file_id>\d+)/$',
                        'processRouteFile', name='process_route_file'),
    # At the end, because it catches large
    url(r'^(?P<area_name>[a-zA-Z0-9_-]+)?', 'index', name="index"),
)
