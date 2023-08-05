#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import lxml.etree
import os
test_path = os.path.abspath(__file__)
test_dir_path = os.path.dirname(test_path) + os.sep

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.template import Context
from django.test import TestCase
from django.test.client import Client

from chimere.admin import managed_modified, MarkerAdmin
from chimere.models import Area, Icon, Importer, Category, SubCategory, Marker,\
                           Route, News
from chimere.forms import MarkerForm, AreaAdminForm
from chimere.templatetags.chimere_tags import display_news
from chimere.utils import ShapefileManager

def areas_setup():
    area_1 = Area.objects.create(name='area 1', urn='area-1', order=1,
                available=True,
                upper_left_corner='SRID=4326;POINT(-4.907753 48.507656)',
                lower_right_corner='SRID=4326;POINT(-4.049447 48.279688)')
    area_2 = Area.objects.create(name='area 2', urn='area-2', order=2,
                available=True,
                upper_left_corner='SRID=4326;POINT(-3 47.5)',
                lower_right_corner='SRID=4326;POINT(-2.5 47)')
    area_3 = Area.objects.create(name='area 3', urn='area-3', order=3,
                available=True,
                upper_left_corner='SRID=4326;POINT(-1.5 1.5)',
                lower_right_corner='SRID=4326;POINT(1.5 -1.5)')
    return [area_1, area_2, area_3]

def subcategory_setup():
    category = Category.objects.create(name='Main category',
                        available=True,
                        order=1,
                        description='')

    icon = Icon.objects.create(name='Default icon',
                               image='icons/marker.png',
                               height=25,
                               width=21)

    subcategory_1 = SubCategory.objects.create(category=category,
                        name='Subcategory 1',
                        available=True,
                        icon=icon,
                        order=1,
                        item_type='M',)

    subcategory_2 = SubCategory.objects.create(category=category,
                        name='Subcategory 2',
                        available=True,
                        icon=icon,
                        order=1,
                        item_type='M',)

    subcategory_3 = SubCategory.objects.create(category=category,
                        name='Subcategory 3',
                        available=True,
                        icon=icon,
                        order=1,
                        item_type='M',)

    subcategory_4 = SubCategory.objects.create(category=category,
                        name='Subcategory 4',
                        available=True,
                        icon=icon,
                        order=1,
                        item_type='M',)
    return [subcategory_1, subcategory_2, subcategory_3, subcategory_4]

def marker_setup(sub_categories=[]):
    if not sub_categories:
        sub_categories = subcategory_setup()
    current_date = datetime.datetime.now()
    markers = []
    marker_1 = Marker.objects.create(name="Marker 1", status='A',
                                     point='SRID=4326;POINT(-4.5 48.4)',
                                     available_date=current_date)
    marker_1.categories.add(sub_categories[0])
    markers.append(marker_1)
    marker_2 = Marker.objects.create(name="Marker 2", status='A',
                                     point='SRID=4326;POINT(-3.5 48.4)',
                                     available_date=current_date,
                                     start_date=current_date)
    marker_2.categories.add(sub_categories[1])
    markers.append(marker_2)
    marker_3 = Marker.objects.create(name="Marker 3", status='A',
                      point='SRID=4326;POINT(-4.5 48.45)',
                      available_date=current_date - datetime.timedelta(days=60),
                      start_date=current_date - datetime.timedelta(days=60),
                      end_date=current_date - datetime.timedelta(days=30))
    marker_3.categories.add(sub_categories[1])
    markers.append(marker_3)
    return markers

def route_setup(sub_categories=[]):
    if not sub_categories:
        sub_categories = subcategory_setup()
    current_date = datetime.datetime.now()
    routes = []
    route_1 = Route.objects.create(name="Route 1", status='A',
         has_associated_marker=True, route='SRID=4326;LINESTRING(-1 1, 1 -1)')
    route_1.categories.add(sub_categories[0])
    routes.append(route_1)
    route_2 = Route.objects.create(name="Route 2", status='A',
        has_associated_marker=False, route='SRID=4326;LINESTRING(0 0, 2 2)')
    route_2.categories.add(sub_categories[1])
    routes.append(route_2)
    return routes

class ImporterTest:
    def test_get(self):
        nb_by_cat = {}
        for importer, awaited_nb in self.marker_importers:
            nb, nb_updated, res = importer.manager.get()
            if awaited_nb == None:
                continue
            self.assertEqual(nb, awaited_nb)
            self.assertEqual(nb_updated, 0)
            for cat in importer.categories.all():
                if cat not in nb_by_cat:
                    nb_by_cat[cat] = 0
                nb_by_cat[cat] += nb
        for cat in nb_by_cat:
            nb = max([Marker.objects.filter(categories__pk=cat.pk).count(),
                      Route.objects.filter(categories__pk=cat.pk).count()])
            self.assertEqual(nb_by_cat[cat], nb)
        # update
        for importer, awaited_nb in self.marker_importers:
            importer.overwrite = True
            importer.save()
            nb, nb_updated, res = importer.manager.get()
            if awaited_nb == None:
                continue
            self.assertEqual(nb, 0)
        # manage overwrite
        for importer, awaited_nb in self.marker_importers:
            if not awaited_nb:
                continue
            # mimic the modification of one item
            for cls in (Marker, Route):
                items = cls.objects.filter(
                                    categories=importer.categories.all()[0]
                                    ).order_by('-pk').all()
                if items.count():
                    item = items.all()[0]
                    item.import_version = 99999 # fake version number
                    item.save()
                    # as when the import_version it is considered as an import
                    # modification force the modification flag
                    item.modified_since_import = True
                    item.save()
            importer.overwrite = False
            importer.save()
            nb, nb_updated, res = importer.manager.get()
            if awaited_nb == None:
                continue
            self.assertEqual(nb, 1)

class KMLImporterTest(TestCase, ImporterTest):
    def setUp(self):
        subcategories = subcategory_setup()
        importer1 = Importer.objects.create(importer_type='KML',
            source=test_dir_path+'tests/sample.kml',
            filtr="Category 1")
        importer1.categories.add(subcategories[0])

        importer2 = Importer.objects.create(importer_type='KML',
         source=test_dir_path+'tests/sample.kml',
         filtr="Subcategory 1", associate_marker_to_way=True)
        importer2.categories.add(subcategories[1])

        importer3 = Importer.objects.create(importer_type='KML',
         source=test_path+'tests/sample.kml',
         filtr="Subcategory 3")
        importer3.categories.add(subcategories[2])

        importer4 = Importer.objects.create(importer_type='KML',
         source=test_dir_path+'tests/sample.kml.zip', zipped=True)
        importer4.categories.add(subcategories[3])

        self.marker_importers = [(importer1, 1), (importer2, 3), (importer3, 0),
                                 (importer4, 4)]

class ShapefileImporterTest(TestCase, ImporterTest):
    def setUp(self):
        self.subcategories = subcategory_setup()
        importer = Importer.objects.create(importer_type='SHP',
            source=test_dir_path+'tests/sample_nodes.shp.zip', zipped=True)
        importer.categories.add(self.subcategories[0])
        importer2 = Importer.objects.create(importer_type='SHP',
            source=test_dir_path+'tests/sample_ways.shp.zip',
            zipped=True)
        importer2.categories.add(self.subcategories[1])

        self.marker_importers = [(importer, 29),
                                 (importer2, 5),]
        self.markers = marker_setup()

    def test_export(self):
        filename, zip_stream = ShapefileManager.export(Marker.objects.all())

    def test_associate_marker_to_way(self):
        importer, nb = self.marker_importers[1]

        importer.associate_marker_to_way = True
        importer.save()
        nb, nb_updated, res = importer.manager.get()
        nb = Marker.objects.filter(categories__pk=self.subcategories[1].pk
                                   ).count()
        self.assertEqual(nb, 5)
        Marker.objects.filter(categories__pk=self.subcategories[1].pk).delete()
        Route.objects.filter(categories__pk=self.subcategories[1].pk).delete()

        importer.associate_marker_to_way = False
        importer.save()
        nb, nb_updated, res = importer.manager.get()
        nb = Marker.objects.filter(categories__pk=self.subcategories[1].pk
                                   ).count()
        self.assertEqual(nb, 0)

class OSMImporterTest(TestCase, ImporterTest):
    def setUp(self):
        subcategories = subcategory_setup()
        markers = marker_setup()
        importer1 = Importer.objects.create(importer_type='OSM',
            source=test_dir_path+'tests/sample_nodes.osm')
        importer1.categories.add(subcategories[0])

        importer2 = Importer.objects.create(importer_type='OSM',
            source=test_dir_path+'tests/sample_ways.osm')
        importer2.categories.add(subcategories[1])

        self.marker_importers = [(importer1, 19), (importer2, 8)]

class GeoRSSImporterTest(TestCase, ImporterTest):
    def setUp(self):
        subcategories = subcategory_setup()
        importer1 = Importer.objects.create(importer_type='RSS',
                         source=test_dir_path+'tests/georss_simple.xml')
        importer1.categories.add(subcategories[0])
        importer2 = Importer.objects.create(importer_type='RSS',
                         source=test_dir_path+'tests/eqs7day-M5.xml')
        importer2.categories.add(subcategories[1])

        self.marker_importers = [(importer1, 1), (importer2, 32)]

class FeedsTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()
        self.markers = marker_setup()

    def test_rss(self):
        # global
        url = reverse('chimere:feeds-global')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        doc = lxml.etree.fromstring(response.content)
        self.assertEqual(int(doc.xpath('count(//item)')), len(self.markers))
        url = reverse('chimere:feeds-areaid', args=('', self.areas[0].pk))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        doc = lxml.etree.fromstring(response.content)
        self.assertEqual(int(doc.xpath('count(//item)')), 2)

class AdminTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()
        self.markers = marker_setup()
        self.adminuser = User.objects.create_superuser('admin',
                                                  'admin@test.com',
                                                  'pass')
        self.client.login(username='admin', password='pass')

    def test_actions(self):
        q_markers = Marker.objects.filter(pk__in=[m.pk for m in self.markers])
        # disable
        response = self.client.post('/admin/chimere/marker/',
                       data={'action':['disable'],
                             '_selected_action':[unicode(m.pk)
                                                 for m in self.markers],
                            })
        self.assertEqual(q_markers.count(),
                         q_markers.filter(status='D').count())
        # validate
        response = self.client.post('/admin/chimere/marker/',
                       data={'action':['validate'],
                             '_selected_action':[unicode(m.pk)
                                                 for m in self.markers]
                            })
        self.assertEqual(q_markers.count(),
                         q_markers.filter(status='A').count())


class MarkerFormTest(TestCase):
    def setUp(self):
        self.subcategories = subcategory_setup()

    def test_marker_creation(self):
        current_date = datetime.datetime.now()
        # end_date before start_date
        data = {'name':"Marker 1", 'status':'A', 'available_date':current_date,
                'point':'SRID=4326;POINT(-4.5 48.4)', 'start_date':current_date,
                'end_date':current_date - datetime.timedelta(1),
                'categories':[self.subcategories[0].pk]}
        form = MarkerForm(data)
        self.assertEqual(form.is_valid(), False)

class AreaTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()

    def test_area_availability(self):
        area_1 = self.areas[0]
        area_1.available = False
        area_1.save()
        response = self.client.get('/%s/' % area_1.urn)
        self.assertRedirects(response, '/')

class AreaAdminFormTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()

    def test_area_default(self):
        area_1, area_2 = self.areas[0], self.areas[1]
        area_1.default = True
        area_1.save()
        area_2.default = True
        area_2.save()
        area_1 = Area.objects.get(urn=area_1.urn)
        self.assertEqual(area_1.default, False)

    def test_area_creation(self):
        base_data = {'name':u'New test', 'order':3, 'available':True,
                'urn':'area-new',
                'upper_left_lat':48.5,
                'upper_left_lon':-5,
                'lower_right_lat':48,
                'lower_right_lon':-4,
                'upper_left_corner':'SRID=4326;POINT(0 0)',
                'lower_right_corner':'SRID=4326;POINT(0 0)'}
        # order already given
        data = base_data.copy()
        data['order'] = self.areas[0].order
        form = AreaAdminForm(data)
        self.assertEqual(form.is_valid(), False)
        # update an already existing area
        data = base_data.copy()
        data['order'] = self.areas[0].order
        form = AreaAdminForm(data, instance=self.areas[0])
        self.assertEqual(form.is_valid(), True)
        # empty area
        data = base_data.copy()
        data.update({'upper_left_lat': 0,
                     'upper_left_lon': 0,
                     'lower_right_lat': 0,
                     'lower_right_lon': 0})
        form = AreaAdminForm(data)
        self.assertEqual(form.is_valid(), False)

class DynamicCategoryTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()
        subcategories = subcategory_setup()
        self.markers = marker_setup(subcategories)
        self.routes = route_setup(subcategories)

    def test_dynamic_evaluation(self):
        cats = self.areas[0].getCategories(status='A', filter_available=True)
        self.assertEqual(len(cats), 1)
        cats = self.areas[2].getCategories(status='A', filter_available=True)
        self.assertEqual(len(cats), 2)

class NewsTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()
        self.markers = marker_setup()
        self.news = []
        self.news.append(News.objects.create(title=u"Test news 1",
                                             available=True))
        self.news.append(News.objects.create(title=u"Test news 2",
                                             available=False))

    def test_news_display(self):
        context = display_news(Context({}))
        self.assertEqual(len(context['news_lst']), 2)
        context = display_news(Context({'area_name':'area-2'}))
        self.assertEqual(len(context['news_lst']), 1)

class RapprochementTest(TestCase):
    def setUp(self):
        self.areas = areas_setup()
        self.subcategories = subcategory_setup()
        self.markers = marker_setup(self.subcategories)
        self.routes = route_setup(self.subcategories)
        self.adminuser = User.objects.create_superuser('admin',
                                                  'admin@test.com',
                                                  'pass')
        self.client.login(username='admin', password='pass')

    def test_managed_modified_markers(self):
        ref_marker = self.markers[0]
        new_vals = {'name':"Marker 1 - modified",
                    'point':GEOSGeometry('SRID=4326;POINT(-4 48)')}
        values = {'status':'M', 'ref_item':ref_marker}
        values.update(new_vals)
        modified_marker = Marker.objects.create(**values)
        modified_marker.categories.add(ref_marker.categories.all()[0])
        response = self.client.post('/admin/chimere/marker/',
                       data={'action':['managed_modified'],
                             'index':0, 'rapprochement':1,
                             'name':1, 'point':1,
                             '_selected_action':[unicode(ref_marker.pk)]
                            })
        ref_marker = Marker.objects.get(pk=ref_marker.pk)
        self.assertEqual(Marker.objects.filter(ref_item=ref_marker,
                                               status='M').count(), 0)
        for k in new_vals:
            self.assertEqual(getattr(ref_marker, k), new_vals[k])

    def test_managed_modified_imported_markers(self):
        ref_marker = self.markers[0]
        new_vals = {'name':"Marker 1 - modified",
                    'point':GEOSGeometry('SRID=4326;POINT(-4 48)')}
        values = {'status':'I', 'ref_item':ref_marker, 'import_version':42}
        values.update(new_vals)
        modified_marker = Marker.objects.create(**values)
        self.assertNotEqual(ref_marker.import_version,
                            modified_marker.import_version)
        modified_marker.categories.add(ref_marker.categories.all()[0])
        response = self.client.post('/admin/chimere/marker/',
                       data={'action':['managed_modified'],
                             'index':0, 'rapprochement':1,
                             'name':1, 'point':1,
                             '_selected_action':[unicode(ref_marker.pk)]
                            })
        ref_marker = Marker.objects.get(pk=ref_marker.pk)
        self.assertEqual(Marker.objects.filter(ref_item=ref_marker,
                                               status='I').count(), 0)
        for k in new_vals.keys() + ['import_version']:
            self.assertEqual(getattr(ref_marker, k), values[k])

    def test_managed_modified_routes(self):
        ref_route = self.routes[0]
        new_vals = {'name':"Route 1 - modified",
                    'route':GEOSGeometry('SRID=4326;LINESTRING(1 1,2 2)')}
        values = {'status':'M', 'ref_item':ref_route,
                  'has_associated_marker':True}
        values.update(new_vals)
        modified_route = Route.objects.create(**values)
        modified_route.categories.add(self.subcategories[1])
        response = self.client.post('/admin/chimere/route/',
                       data={'action':['managed_modified'],
                             'index':0, 'rapprochement':1,
                             'name':1, 'route':1, 'categories':1,
                             '_selected_action':[unicode(ref_route.pk)]
                            })
        ref_route = Route.objects.get(pk=ref_route.pk)
        self.assertEqual(Route.objects.filter(ref_item=ref_route,
                                               status='M').count(), 0)
        self.assertEqual(ref_route.name, new_vals['name'])
        self.assertEqual(ref_route.route.wkt, new_vals['route'].wkt)
        self.assertEqual(ref_route.categories.all()[0], self.subcategories[1])
        self.assertEqual(ref_route.associated_marker.all()[0].name,
                         ref_route.name)

class RouteTest(TestCase):
    def setUp(self):
        self.subcategories = subcategory_setup()

    def test_route_creation(self):
        route_1 = Route.objects.create(name='Route 1',
                      route='SRID=4326;LINESTRING (30 10, 10 30, 40 40)')
        self.assertEqual(Marker.objects.filter(route=route_1).count(), 1)
        route_2 = Route.objects.create(name='Route 1',
                      route='SRID=4326;LINESTRING (30 10, 10 30, 40 40)',
                      has_associated_marker=False)
        self.assertEqual(Marker.objects.filter(route=route_2).count(), 0)
