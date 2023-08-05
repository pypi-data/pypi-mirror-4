#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
Utilitaries
"""

import csv
import datetime
import feedparser
import os
import re
import StringIO
import tempfile
import urllib2
import unicodedata
import zipfile

from osgeo import ogr, osr
from lxml import etree

from django.conf import settings
from django.contrib.gis.gdal import DataSource, OGRGeomType, check_err
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.utils.translation import ugettext_lazy as _

from chimere import get_version
from external_utils import OsmApi

def unicode_normalize(string):
    return ''.join(
        (c for c in unicodedata.normalize('NFD', string)
        if unicodedata.category(c) != 'Mn'))

class ImportManager:
    u"""
    Generic class for specific importers
    """
    default_source = None
    def __init__(self, importer_instance):
        self.importer_instance = importer_instance
        if self.importer_instance.default_name:
            self.default_name = self.importer_instance.default_name
        else:
            self.default_name = " - ".join([cat.name
                for cat in self.importer_instance.categories.order_by(
                                                               'name').all()])

    def get(self):
        pass

    def put(self, extra_args={}):
        pass

    def create_or_update_item(self, cls, values, import_key, version=None,
                              key='', pk=None):
        updated, created, item = False, False, None
        import_key = unicode(import_key).replace(':', '^')
        if not key:
            key = self.importer_instance.importer_type
        if import_key or pk:
            dct_import = {
                'import_key__icontains':'%s:%s;' % (key, import_key),
                'import_source':self.importer_instance.source}
            try:
                if pk:
                    ref_item = cls.objects.get(pk=pk)
                else:
                    ref_item = cls.objects.get(**dct_import)
                if version and ref_item.import_version == int(version):
                    # no update since the last import
                    return ref_item, None, None
                if not self.importer_instance.overwrite \
                   and ref_item.modified_since_import:
                    dct_import['ref_item'] = ref_item
                else:
                    item = ref_item
                    for k in values:
                        setattr(item, k, values[k])
                    try:
                        item.save()
                        # force the modified_since_import status
                        item.modified_since_import = False
                        item.save()
                    except TypeError:
                        # error on data source
                        return None, False, False
                    updated = True
            except ObjectDoesNotExist:
                pass
        if not item:
            values.update({
                'import_source':self.importer_instance.source})
            values['status'] = 'I'
            if not self.importer_instance.associate_marker_to_way\
              and cls.__name__ == 'Route':
                values['has_associated_marker'] = False
            try:
                item = cls.objects.create(**values)
            except TypeError:
                # error on data source
                return None, False, False
            created = True
        if import_key:
            item.set_key(key, import_key)
        item.categories.clear()
        for cat in self.importer_instance.categories.all():
            item.categories.add(cat)
        return item, updated, created

    @classmethod
    def get_files_inside_zip(cls, zippedfile, suffixes, dest_dir=None):
        try:
            flz = zipfile.ZipFile(zippedfile)
        except zipfile.BadZipfile:
            return [], _(u"Bad zip file")
        namelist = flz.namelist()
        filenames = []
        for suffix in suffixes:
            current_file_name = None
            for name in namelist:
                if name.endswith(suffix) \
                  or name.endswith(suffix.lower()) \
                  or name.endswith(suffix.upper()):
                    current_file_name = name
            filenames.append(current_file_name)
        files = []
        for filename in filenames:
            if filename:
                if dest_dir:
                    files.append(filename)
                    flz.extract(filename, dest_dir)
                else:
                    files.append(flz.open(filename))
            else:
                files.append(None)
        return files

    def get_source_file(self, suffixes, dest_dir=None,
                        extra_url=None):
        source = self.importer_instance.source_file
        if not hasattr(source, 'read'):
            if not source:
                source = self.importer_instance.source \
                       if self.importer_instance.source else self.default_source
            try:
                url = source
                if extra_url:
                    url += extra_url
                remotehandle = urllib2.urlopen(url)
                source = StringIO.StringIO(remotehandle.read())
                remotehandle.close()
            except ValueError:
                # assume it is a local file
                try:
                    source = open(source)
                except IOError, msg:
                    return (None, msg)
            except (urllib2.URLError, AttributeError) as error:
                return (None, error.message)
        if self.importer_instance.zipped:
            try:
                files = self.get_files_inside_zip(source, suffixes, dest_dir)
            except zipfile.BadZipfile:
                return (None, _(u"Bad zip file"))
            if not files or None in files:
                return (None,
                        _(u"Missing file(s) inside the zip file"))
            source = files[0] if len(suffixes) == 1 else files
        return (source, None)

class KMLManager(ImportManager):
    u"""
    KML importer
    The filtr argument has to be defined as the exact name of the folder to be
    imported
    """
    XPATH = '//kml:Folder/kml:name[text()="%s"]/../kml:Placemark'
    DEFAULT_XPATH = '//kml:Placemark'
    def __init__(self, importer_instance, ns=''):
        self.importer_instance = importer_instance
        self.ns = ns

    def get(self):
        u"""
        Get data from a KML source

        Return a tuple with:
         - number of new item ;
         - number of item updated ;
         - error detail on error
        """
        from models import Marker, Route
        new_item, updated_item, msg = 0, 0, ''
        source, msg = self.get_source_file(['.kml'])
        if msg:
            return (0, 0, msg)
        doc = source
        # remove empty lines before declaration (bad XML file)
        if hasattr(source, 'getvalue'):
            splitted = source.getvalue().split('\n')
            for idx, line in enumerate(splitted):
                if line.strip():
                    break
            doc = StringIO.StringIO("\n".join(splitted[idx:]))
        try:
            tree = etree.parse(doc)
        except:
            return (0, 0, _(u"Bad XML file"))
        # try to get default namespace
        if not self.ns:
            self.ns = tree.getroot().nsmap[None]
        xpath = self.XPATH % self.importer_instance.filtr \
                  if self.importer_instance.filtr else self.DEFAULT_XPATH
        for placemark in tree.xpath(xpath,
                                    namespaces={'kml':self.ns}):
            name, point, line = None, None, None
            pl_id = placemark.attrib.get('id')
            pl_key = 'kml-%d' % self.importer_instance.pk
            ns = '{%s}' % self.ns
            for item in placemark:
                if item.tag == ns + 'name':
                    name = item.text
                    if not pl_id:
                        # if no ID is provided assume that name is a key
                        pl_id = name
                elif item.tag == ns + 'description':
                    description = item.text
                elif item.tag == ns + 'Point':
                    for coord in item:
                        if coord.tag == ns + 'coordinates':
                            x, y, z = coord.text.split(',')
                            point = 'SRID=4326;POINT(%s %s)' % (x, y)
                elif item.tag == ns + 'LineString':
                    for coord in item:
                        if coord.tag == ns + 'coordinates':
                            points = coord.text.replace('\n', ' ').split(' ')
                            points = ",".join([" ".join(p.split(',')[:2])
                                               for p in points if p])
                            line = 'SRID=4326;LINESTRING(%s)' % points
            cls = None
            dct = {'description':description,
                   'name':name,
                   'origin':self.importer_instance.origin,
                   'license':self.importer_instance.license}
            if point:
                dct['point'] = point
                cls = Marker
            if line:
                dct['route'] = line
                dct.pop('description')
                cls = Route
            if cls:
                item, updated, created = self.create_or_update_item(
                                                cls, dct, pl_id, key=pl_key)
                if updated:
                    updated_item += 1
                if created:
                    new_item += 1
        return (new_item, updated_item, msg)

    @classmethod
    def export(cls, queryset):
        dct = {'name':settings.PROJECT_NAME,
               'description':unicode(datetime.date.today()),
               'locations':queryset.all()
        }
        filename = unicode_normalize(settings.PROJECT_NAME + dct['description']\
                                     + '.kml')
        result = render_to_response('chimere/export.kml', dct)
        return filename, result

class ShapefileManager(ImportManager):
    u"""
    Shapefile importer
    """
    def get(self):
        u"""
        Get data from a Shapefile source

        Return a tuple with:
         - number of new item ;
         - number of item updated ;
         - error detail on error
        """
        from models import Marker, Route
        new_item, updated_item, msg = 0, 0, ''
        tmpdir = tempfile.mkdtemp()
        sources, msg = self.get_source_file(['.shp', '.dbf', '.prj', '.shx'],
                                            dest_dir=tmpdir)
        if msg:
            return (0, 0, msg)
        if not sources:
            return (0, 0, _(u"Error while reading the data source."))
        # get the srid
        srid = self.importer_instance.srid
        if not srid:
            prjfilename = tmpdir + os.sep + sources[2]
            try:
                from osgeo import osr
                with open(prjfilename, 'r') as prj_file:
                    prj_txt = prj_file.read()
                    srs = osr.SpatialReference()
                    srs.ImportFromESRI([prj_txt])
                    srs.AutoIdentifyEPSG()
                    srid = srs.GetAuthorityCode(None)
            except ImportError:
                pass
            if not srid:
                # try with the default projection
                srid = settings.CHIMERE_EPSG_DISPLAY_PROJECTION
                msg = _(u"SRID cannot be guessed. The default SRID (%s) has "
                        u"been used.") % srid
                #If imported items are not well located "
                #        u"ask your data provider for the SRID to use.") % srid
        shapefilename = tmpdir + os.sep + sources[0]
        ds = DataSource(shapefilename)
        lyr = ds[0]
        # for this first version it is assumed that the first field is a
        # id name and the second field is the name
        id_name = lyr.fields[0] if len(lyr.fields) > 0 else None
        # test if id_name is well guess
        if id_name:
            ids = lyr.get_fields(id_name)
            if len(ids) != len(set(ids)):
                id_name = None
        lbl_name = None
        if len(lyr.fields) > 1:
            lbl_name = lyr.fields[1]
        elif id_name:
            lbl_name = id_name
        if lyr.geom_type not in ('Point', 'LineString'):
            return (0, 0, _(u"Type of geographic item of this shapefile "
                            u"is not managed by Chimère."))
        geom_key = 'point' if lyr.geom_type == 'Point' else 'route'
        geom_cls = Marker if lyr.geom_type == 'Point' else Route
        indexes = []
        for idx, feat in enumerate(lyr):
            name = unicode(idx)
            if lbl_name:
                name = feat.get(lbl_name)
                try:
                    name = unicode(name)
                except UnicodeDecodeError:
                    try:
                        name = unicode(
                               name.decode(settings.CHIMERE_SHAPEFILE_ENCODING))
                    except:
                        continue
            try:
                geoms = [feat.geom.wkt]
            except:
                return (0, 0, _(u"Bad Shapefile"))
            if feat.geom.geom_type == 'MultiLineString':
                geoms = [geom.wkt for geom in feat.geom]
            import_key = feat.get(id_name) if id_name and len(geoms) == 1 else ''
            for geom in geoms:
                dct = {geom_key:'SRID=%s;%s' % (srid, geom),
                   'name':name,
                   'origin':self.importer_instance.origin,
                   'license':self.importer_instance.license
                  }
                item, updated, created = self.create_or_update_item(
                                    geom_cls, dct, import_key)
                if updated:
                    updated_item += 1
                if created:
                    new_item += 1
        # clean up
        tmpdirs = set()
        for src in sources:
            dirs = os.sep.join(src.split(os.sep)[:-1])
            if dirs:
                tmpdirs.add(tmpdir + os.sep + dirs)
            os.remove(tmpdir + os.sep + src)
        for dr in tmpdirs:
            os.removedirs(dr)
        return (new_item, updated_item, msg)

    @classmethod
    def export(cls, queryset):
        date = unicode(datetime.date.today())

        tmp = tempfile.NamedTemporaryFile(suffix='.shp', mode='w+b')
        tmp.close()

        tmp_name = tmp.name
        field_names = [field.name for field in queryset.model._meta.fields]
        geo_field = getattr(queryset.model,
                          'point' if 'point' in field_names else 'route')._field

        dr = ogr.GetDriverByName('ESRI Shapefile')
        ds = dr.CreateDataSource(tmp_name)
        if ds is None:
            raise Exception(_(u'Could not create file!'))
        ogr_type = OGRGeomType(geo_field.geom_type).num
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(geo_field.srid)

        layer = ds.CreateLayer('lyr', srs=srs, geom_type=ogr_type)

        for field_name in ('name', 'category'):
            field_defn = ogr.FieldDefn(str(field_name), ogr.OFTString)
            field_defn.SetWidth(255)
            if layer.CreateField(field_defn) != 0:
                raise Exception(_(u'Failed to create field'))

        feature_def = layer.GetLayerDefn()

        for item in queryset:
            # duplicate items when in several categories
            for category in item.categories.all():
                feat = ogr.Feature(feature_def)
                feat.SetField('name', str(unicode_normalize(item.name)[:80]))
                feat.SetField('category',
                                   str(unicode_normalize(category.name)[:80]))

                geom = getattr(item, geo_field.name)
                if not geom:
                    continue
                ogr_geom = ogr.CreateGeometryFromWkt(geom.wkt)
                check_err(feat.SetGeometry(ogr_geom))
            check_err(layer.CreateFeature(feat))
        # Cleaning up
        ds.Destroy()

        # writing to a zip file
        filename = unicode_normalize(settings.PROJECT_NAME) + '-' + date
        buff = StringIO.StringIO()
        zip_file = zipfile.ZipFile(buff, 'w', zipfile.ZIP_DEFLATED)
        suffixes = ['shp', 'shx', 'prj', 'dbf']
        for suffix in suffixes:
            name = tmp_name.replace('.shp', '.' + suffix)
            arcname = '.'.join((filename, suffix))
            zip_file.write(name, arcname=arcname)
        zip_file.close()
        buff.flush()
        zip_stream = buff.getvalue()
        buff.close()
        return filename, zip_stream

class CSVManager(ImportManager):
    u"""
    CSV importer
    """
    @classmethod
    def set_categories(value):
        return

    # (label, getter, setter)
    COLS = [("Id", 'pk', 'pk'), (_(u"Name"), 'name', 'name'),
            (_(u"Categories"), lambda obj:", ".join(
                                [c.name for c in obj.categories.all()]),
                                set_categories),
            (_(u"State"), 'status', lambda x: x),
            (_(u"Description"), 'description', 'description'),
            (_(u"Localisation"), 'geometry', 'geometry')]

    def get(self):
        u"""
        Get data from a CSV source

        Return a tuple with:
         - number of new item ;
         - number of item updated ;
         - error detail on error
        """
        from models import Marker, Route
        new_item, updated_item, msg = 0, 0, ''
        source, msg = self.get_source_file(['.csv'])
        if msg:
            return (0, 0, msg)
        reader = csv.reader(source, delimiter=';', quotechar='"')
        prop_cols = []
        for pm in Marker.properties():
            prop_cols.append((pm.name, pm.getAttrName(),
                              pm.getAttrName()+'_set'))
        cols = self.COLS + prop_cols
        datas = []
        for idx, row in enumerate(reader):
            if not idx: # first row
                try:
                    assert(len(row) >= len(cols))
                except AssertionError:
                    return (0, 0, _(u"Invalid CSV format"))
                continue
            if len(row) < len(cols):
                continue
            pk, name, cats, state = row[0], row[1], row[2], row[3]
            description, geom = row[4], row[5]
            COL_INDEX = 6
            dct = {'description':description,
                   'name':name,
                   'origin':self.importer_instance.origin,
                   'license':self.importer_instance.license}
            cls = None
            if 'POINT' in geom:
                cls = Marker
                dct['point'] = geom
            elif 'LINE' in geom:
                cls = Route
                dct['route'] = geom
            else:
                continue
            import_key = pk if pk else name
            item, updated, created = self.create_or_update_item(cls, dct,
                                                             import_key, pk=pk)
            if updated:
                updated_item += 1
            if created:
                new_item += 1
            for idx, col in enumerate(cols[COL_INDEX:]):
                name, getter, setter_val = col
                setter = getattr(item, setter_val)
                val = row[idx+COL_INDEX]
                setter(item, val)
        return (new_item, updated_item, msg)

    @classmethod
    def export(cls, queryset):
        dct = {'description':unicode(datetime.date.today()), 'data':[]}
        cls_name = queryset.model.__name__.lower()
        cols = cls.COLS
        for pm in queryset.model.properties():
            cols.append((pm.name, pm.getAttrName(), pm.getAttrName()+'_set'))
        header = [col[0] for col in cols]
        dct['data'].append(header)
        for item in queryset.all():
            data = []
            for (lbl, attr, setr) in cols:
                if callable(attr):
                    data.append(attr(item))
                else:
                    data.append(getattr(item, attr))
            dct['data'].append(data)
        filename = unicode_normalize(settings.PROJECT_NAME + dct['description']\
                                     + '.csv')
        result = render_to_response('chimere/export.csv', dct)
        return filename, result

class GeoRSSManager(ImportManager):
    u"""
    RSS importer.
    This manager only gets and do not produce GeoRSSFeed
    """

    def get(self):
        u"""
        Get data from a GeoRSS simple source

        Return a tuple with:
         - number of new item ;
         - number of item updated ;
         - error detail on error
        """
        from models import Marker
        new_item, updated_item, msg = 0, 0, ''
        feed = feedparser.parse(self.importer_instance.source)
        if feed['bozo']:
            return (0, 0, _(u"RSS feed is not well formed"))
        for item in feed['items']:
            if "georss_point" not in item and 'georss_line' not in item \
               and not ("geo_lat" in item and "geo_long" in item):
                continue
            cls = None
            dct = {'origin':self.importer_instance.origin,
                   'license':self.importer_instance.license}
            if 'georss_point' in item or "geo_lat" in item:
                cls = Marker
                if 'georss_point' in item:
                    try:
                        y, x = item['georss_point'].split(' ')
                    except ValueError:
                        continue
                else:
                    y = item['geo_lat']
                    x = item['geo_long']
                dct['point'] = 'SRID=4326;POINT(%s %s)' % (x, y)
                for k in ['description', 'summary', 'value']:
                    if k in item:
                        dct['description'] = item[k]
                        break
            else:
                cls = Route
                points = item['georss_line'].split(' ')
                reordered_points = []
                # lat, lon -> x, y
                for idx in xrange(len(points)/2):
                    reordered_points.append("%s %s" % (points[idx*2+1],
                                                       points[idx*2]))
                dct['route'] = 'SRID=4326;LINESTRING(%s)' % \
                            ",".join(reordered_points)

            dct['name'] = item['title']
            pl_id = item['id'] if 'id' in item else item['title']
            it, updated, created = self.create_or_update_item(cls, dct, pl_id)
            if updated:
                updated_item += 1
            if created:
                new_item += 1
        return (new_item, updated_item, msg)

RE_HOOK = re.compile('\[([^\]]*)\]')

# TODO: manage deleted item from OSM

class OSMManager(ImportManager):
    u"""
    OSM importer/exporter
    The source url is a path to an OSM file or a XAPI url
    The filtr argument is XAPI args or empty if it is an OSM file.
    """
    default_source = settings.CHIMERE_XAPI_URL

    def get(self):
        u"""
        Get data from the source

        Return a tuple with:
        - new items;
        - updated items;
        - error detail on error.
        """
        source, msg = self.get_source_file(['.osm'],
                                         extra_url=self.importer_instance.filtr)
        if not source:
            return (0, 0, msg)

        tree = etree.parse(source)
        # only import node or ways
        if tree.xpath('count(//way)') and tree.xpath('count(//node)'):
            return self.import_ways(tree)
        elif tree.xpath('count(//node)'):
            return self.import_nodes(tree)
        return 0, 0, _(u"Nothing to import")

    def import_ways(self, tree):
        from chimere.models import Marker, Route
        msg, items, new_item, updated_item = "", [], 0 , 0
        nodes = {}
        for node in tree.xpath('//node'):
            node_id = node.attrib.get('id')
            for item in node:
                k = item.attrib.get('k')
            if node_id:
                nodes[node_id] = '%s %s' % (node.get('lon'),
                                            node.get('lat'))
        for way in tree.xpath('//way'):
            name = None
            points = []
            node_id = way.attrib.get('id')
            version = way.attrib.get('version')
            for item in way:
                k = item.attrib.get('k')
                if k == 'name':
                    name = item.attrib.get('v')
                if item.tag == 'nd':
                    points.append(item.get('ref'))
            if not name:
                name = self.default_name
            if not points:
                continue
            wkt = 'SRID=4326;LINESTRING(%s)' % ",".join([nodes[point_id]
                            for point_id in points if point_id in nodes])
            dct = {'route':wkt,
                   'name':name,
                   'origin':self.importer_instance.origin \
                            or u'OpenStreetMap.org',
                   'license':self.importer_instance.license \
                             or u'ODbL',
                   'import_version':version}
            item, updated, created = self.create_or_update_item(
                                    Route, dct, node_id, version)
            if updated:
                updated_item += 1
            if created:
                new_item += 1
            items.append(item)
        return new_item, updated_item, msg

    def import_nodes(self, tree):
        from chimere.models import Marker
        msg, items, new_item, updated_item = "", [], 0 , 0
        for node in tree.xpath('//node'):
            name = None
            node_id = node.attrib.get('id')
            if not node_id:
                continue
            version = node.attrib.get('version')
            for item in node:
                k = item.attrib.get('k')
                if k == 'name':
                    name = item.attrib.get('v')
            if not name:
                name = self.default_name
            point = 'SRID=4326;POINT(%s %s)' % (node.get('lon'),
                                                node.get('lat'))
            dct = {'point':point,
                   'name':name,
                   'origin':self.importer_instance.origin \
                            or u'OpenStreetMap.org',
                   'license':self.importer_instance.license \
                             or u'ODbL',
                   'import_version':version}
            item, updated, created = self.create_or_update_item(
                                    Marker, dct, node_id, version)
            if updated:
                updated_item += 1
            if created:
                new_item += 1
            items.append(item)
        return (new_item, updated_item, msg)

    def put(self, extra_args={}):
        # first of all: reimport in order to verify that no changes has been
        # made since the last import
        from models import Marker
        new_item, updated_item, msg = self.get()
        # check if import is possible
        if msg:
            return 0, msg
        if new_item:
            return 0, _(u"New items imported - validate them before exporting")
        if Marker.objects.filter(status='I').count():
            return 0, _(u"There are items from a former import not yet "
                        u"validated - validate them before exporting")
        # start import
        api = settings.CHIMERE_OSM_API_URL
        username = settings.CHIMERE_OSM_USER
        password = settings.CHIMERE_OSM_PASSWORD
        if extra_args:
            try:
                api = extra_args['api']
                username = extra_args['username']
                password = extra_args['password']
            except KeyError:
                return 0, _(u"Bad params - programming error")
        username = username.encode('latin1')
        password = password.encode('latin1')
        api = OsmApi.OsmApi(api=api, username=username, password=password)
        api.ChangesetCreate({u"comment": u"Import from Chimère %s" % \
                                                            get_version()})
        hooks = RE_HOOK.findall(self.importer_instance.filtr)
        if not hooks:
            hooks = RE_HOOK.findall(self.importer_instance.source)
            if not hooks:
                return 0, _(u"Bad param")
        tags = {}
        bbox = []
        for hook in hooks:
            key, value = hook.split('=')
            if '*' in value or '|' in key or '|' in value:
                continue
            if key == 'bbox':
                x1, y1, x2, y2 = [float(val) for val in value.split(',')]
                bbox =  GEOSGeometry(
                    'POLYGON((%f %f,%f %f,%f %f,%f %f,%f %f))' % (
                    x1, y1, x2, y1, x2, y2, x1, y2, x1, y1), srid=4326)
                continue
            tags[key] = value
        if not tags:
            return 0, _(u"No non ambigious tag is defined in the XAPI request")
        if not bbox:
            return 0, _(u"No bounding box is defined in the XAPI request."\
            u"If you are sure to manage the entire planet set the bounding box"\
            u" to -180,-90,180,90")
        default_dct = {'tag':tags,
                       'import_source':self.importer_instance.source}
        idx = -1
        for idx, item in enumerate(Marker.objects.filter(status='A',
                point__contained=bbox,
                categories=self.importer_instance.categories.all(),
                not_for_osm=False, modified_since_import=True,
                route=None).all()):
            dct = default_dct.copy()
            dct.update({'lon':item.point.x,
                        'lat':item.point.y})
            dct['tag']['name'] = item.name
            node = None
            import_key = item.get_key('OSM')
            updated = False
            if import_key:
                try:
                    dct['id'] = import_key
                    dct['version'] = item.import_version
                    node = api.NodeUpdate(dct)
                    updated = True
                except OsmApi.ApiError, error:
                    if error.status == 404:
                        dct.pop('id')
                        dct.pop('version')
                        pass # if the node doesn't exist it is created
                    else:
                        raise
            if not updated:
                node = api.NodeCreate(dct)
                item.set_key('OSM', node['id'])
            item.import_version = node['version']
            item.save()
        api.ChangesetClose()
        return idx+1, None
