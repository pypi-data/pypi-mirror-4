#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Étienne Loks <etienne.loks_AT_peacefrogsDOTnet>
# Copyright (C) 2010 Pierre Clarenc <pierre.crc_AT_gmailDOTcom>,
#                    Samuel Renard <renard.samuel_AT_gmailDOTcom>

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
from django.contrib.gis.geos import *
from django.contrib.gis.feeds import Feed
from django.contrib.syndication.views import FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from django.shortcuts import get_object_or_404

from chimere.models import Category, SubCategory, Marker, Area

class BaseFeed(Feed):
    """
    Base feed for Chimere objects
    """
    def item_link(self, item):
        ''' Return POI permalink '''
        coord = item.point
        cat = 0
        if item.categories.all() and item.categories.all()[0]:
            cat = item.categories.all()[0].pk
        return reverse('chimere:index') + '?zoom=16&lat=%f&lon=%f&'\
        'current_feature=%d&checked_categories=%d' % (coord.y, coord.x, item.id,
                                                      cat)

    def item_pubdate(self, item):
        """
        Date of the Marker when it has been available
        """
        return item.available_date

    def description(self, obj):
        return ""

    def item_geometry(self, obj):
        return obj.point

class LatestPOIsByCategory(BaseFeed):
    '''
    Last Points of interests by category in Feeds
    '''
    title_template = "chimere/feeds/rss_title.html"
    description_template = "chimere/feeds/rss_descr.html"

    def get_object(self, request, category_id, area_name=''):
        return get_object_or_404(Category, id=category_id)

    def title(self, obj):
        """
        Define the title of the feed
        """
        return u"%s - %s" % (settings.PROJECT_NAME, obj.name)

    def link(self, obj):
        """
        Define the link of the feed.
        """
        if not obj:
            raise FeedDoesNotExist
        return reverse('chimere:feeds-cat', args=['', obj.id])

    def items(self, obj):
        """
        Requests to marker where its category match the category is requested
        and its status is available
        This returns a list of the 15 last markers/POIs ordering by date
        """
        q = Marker.objects.filter(status__exact='A',
            categories__category__id__exact=obj.id,
            available_date__isnull=False).order_by('-available_date')[:15]
        return q

class LatestPOIsBySubCategory(BaseFeed):
    '''
    Last Points of interests by SubCategory in Feeds
    '''
    title_template = "chimere/feeds/rss_title.html"
    description_template = "chimere/feeds/rss_descr.html"

    def get_object(self, request, category_id, area_name=''):
        return get_object_or_404(SubCategory, id=category_id)

    def title(self, obj):
        return u"%s - %s - %s" % (settings.PROJECT_NAME, obj.category.name,
                                  obj.name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('chimere:feeds-subcat', args=['', obj.id])

    def items(self, obj):
        q = Marker.objects.filter(categories__id__exact=obj.id,
            available_date__isnull=False, status__exact='A').order_by(
                                                        '-available_date')[:15]
        return q

class LatestPOIs(BaseFeed):
    '''
    Last Points of interests
    '''
    title_template = "chimere/feeds/rss_title.html"
    description_template = "chimere/feeds/rss_descr.html"

    def title(self):
        return settings.PROJECT_NAME + u" - " + _(u"Last points of interest")

    def link(self):
        return reverse('chimere:feeds-global')

    def description(self):
        return _("Latest points of interest from ") + settings.PROJECT_NAME

    def items(self):
        q = Marker.objects.filter(status__exact='A',
                  available_date__isnull=False).order_by('-available_date')[:15]
        return q

class LatestPOIsByZone(BaseFeed):
    '''
    Last Points of interests by zone by coordinates
    '''
    title_template = "chimere/feeds/rss_title.html"
    description_template = "chimere/feeds/rss_descr.html"
    upper_left_lat = 0
    upper_left_lon = 0
    lower_right_lat = 0
    lower_right_lon = 0

    def get_object(self, request, area, area_name=''):
        """
        Get the extra url. Parameters are the coordinates of the zone (the
        upper left and lower right points)
        """
        if not area:
            raise ObjectDoesNotExist
        # Then define the upper right and lower left points
        coordinates = str(area).split('_')
        upper_left_lat = float(coordinates[0])
        upper_left_lon = float(coordinates[1])
        lower_right_lat = float(coordinates[2])
        lower_right_lon = float(coordinates[3])
        upper_right_lat = upper_left_lat
        upper_right_lon = lower_right_lon
        lower_left_lat = lower_right_lat
        lower_left_lon = upper_left_lon
        # Define a Polygon with the 4 points of the zone.
        areaBox = Polygon(((upper_left_lon, upper_left_lat),
                            (upper_right_lon, upper_right_lat),
                            (lower_right_lon, lower_right_lat),
                            (lower_left_lon, lower_left_lat),
                            (upper_left_lon, upper_left_lat)),
                            srid=settings.CHIMERE_EPSG_DISPLAY_PROJECTION)
        return areaBox

    def title(self, obj):
        return settings.PROJECT_NAME + u" - " +\
               _(u"Last points of interest by area")

    def link(self, obj):
        """
        Define the link of the feed. It's the same url as we get in the method
        get_object
        """
        if not obj:
            raise FeedDoesNotExist
        area = str(self.upper_left_lat) + '_' + str(self.upper_left_lon) + \
               '_' + str(self.lower_right_lat) + '_' + str(self.lower_right_lon)
        return reverse('chimere:feeds-area', args=['', area])

    def items(self, obj):
        """
        Request to return Markers WHERE there points are containes in the zone
        which is requested.
        This returns a list of the 15 last markers/POIs ordering by date
        """
        q = Marker.objects.filter(point__contained=obj, status__exact='A',
                  available_date__isnull=False).order_by('-available_date')[:15]
        return q

class LatestPOIsByZoneID(BaseFeed):
    '''
    Last Points of interests by zone by id
    '''
    title_template = "chimere/feeds/rss_title.html"
    description_template = "chimere/feeds/rss_descr.html"

    def get_object(self, request, area_id, area_name=''):
        return get_object_or_404(Area, id=area_id)

    def title(self, obj):
        return settings.PROJECT_NAME + u" - " + \
              _(u"Last points of interest") + u" - " + obj.name

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return reverse('chimere:feeds-areaid', args=['', obj.id])

    def items(self, obj):
        q = Marker.objects.filter(available_date__isnull=False, status='A')
        q = q.filter(obj.getIncludeMarker()).order_by('-available_date')[:15]
        return q
