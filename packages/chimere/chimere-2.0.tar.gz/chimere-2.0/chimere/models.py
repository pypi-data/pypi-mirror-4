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
Models description
"""
import os, datetime, pyexiv2, re, string
import simplejson as json
from lxml import etree
from PIL import Image
from subprocess import Popen, PIPE
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Permission, ContentType, Group
from django.contrib.gis.db import models
from django.contrib.gis.gdal import SpatialReference
from django.core.files import File
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.template import defaultfilters
from django.utils.translation import ugettext_lazy as _

from chimere.widgets import PointField, RouteField, SelectMultipleField, \
                            TextareaWidget, DatePickerWidget
from chimere.managers import BaseGeoManager
from chimere.utils import KMLManager, OSMManager, ShapefileManager, \
                          GeoRSSManager, CSVManager

class News(models.Model):
    """News of the site
    """
    title = models.CharField(_(u"Name"), max_length=150)
    available = models.BooleanField(_(u"Available"))
    date = models.DateField(_(u"Date"), auto_now_add=True)
    content = models.TextField()
    areas = SelectMultipleField('Area', verbose_name=_(u"Associated areas"),
                                blank=True, null=True)
    def __unicode__(self):
        ordering = ["-date"]
        return self.title
    class Meta:
        verbose_name = _(u"News")
        verbose_name_plural = _(u"News")

class TinyUrl(models.Model):
    """Tinyfied version of permalink parameters
    """
    parameters = models.CharField(_(u"Parameters"), max_length=500)
    def __unicode__(self):
        return self.parameters
    class Meta:
        verbose_name = _(u"TinyUrl")
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(digits)

    @classmethod
    def getParametersByUrn(cls, urn):
        c_id = 0
        for idx, char in enumerate(reversed(urn)):
            c_id += cls.digits.index(char)*pow(cls.base, idx)
        try:
            params = cls.objects.get(id=c_id).parameters
        except cls.DoesNotExist:
            return ''
        return params

    @classmethod
    def getUrnByParameters(cls, parameters):
        try:
            obj = cls.objects.get(parameters=parameters)
        except cls.DoesNotExist:
            obj = cls(parameters=parameters)
            obj.save()
        n = obj.id
        urn = ''
        while 1:
            idx = n % cls.base
            urn = cls.digits[idx] + urn
            n = n / cls.base
            if n == 0:
                break
        return urn

class ColorTheme(models.Model):
    """Color theme
    """
    name = models.CharField(_(u"Name"), max_length=150)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = _(u"Color theme")

class Color(models.Model):
    """Color
    """
    code = models.CharField(_(u"Code"), max_length=6)
    order = models.IntegerField(_(u"Order"))
    color_theme = models.ForeignKey(ColorTheme, verbose_name=_(u"Color theme"))
    def __unicode__(self):
        return self.code
    class Meta:
        ordering = ["order"]
        verbose_name = _(u"Color")

class Category(models.Model):
    """Category of Point Of Interest (POI)
    """
    name = models.CharField(_(u"Name"), max_length=150)
    available = models.BooleanField(_(u"Available"))
    order = models.IntegerField(_(u"Order"))
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ["order"]
        verbose_name = _(u"Category")

class Icon(models.Model):
    '''Icon
    '''
    name = models.CharField(_(u"Name"), max_length=150)
    image = models.ImageField(_(u"Image"), upload_to='icons',
                              height_field='height', width_field='width')
    height = models.IntegerField(_(u"Height"))
    width = models.IntegerField(_(u"Width"))
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = _(u"Icon")

class SubCategory(models.Model):
    '''Sub-category
    '''
    category = models.ForeignKey(Category, verbose_name=_(u"Category"),
                                 related_name='subcategories')
    name = models.CharField(_(u"Name"), max_length=150)
    available = models.BooleanField(_(u"Available"), default=True)
    submission = models.BooleanField(_(u"Available for submission"),
                                     default=True)
    icon = models.ForeignKey(Icon, verbose_name=_(u"Icon"))
    color_theme = models.ForeignKey(ColorTheme, verbose_name=_(u"Color theme"),
                                    blank=True, null=True)
    order = models.IntegerField(_(u"Order"), default=1000)
    TYPE = (('M', _(u'Marker')),
            ('R', _(u'Route')),
            ('B', _(u'Both')),)
    item_type = models.CharField(_(u"Item type"), max_length=1, choices=TYPE)
    def __unicode__(self):
        return u"%s / %s" % (self.category.name, self.name)
    class Meta:
        ordering = ["category", "order"]
        verbose_name = _(u"Sub-category")
        verbose_name_plural = _(u"Sub-categories")

    @classmethod
    def getAvailable(cls, item_types=None, area_name=None, public=False):
        '''Get list of tuples with first the category and second the associated
        subcategories
        '''
        sub_categories = {}
        subcategories = cls.objects.filter(category__available=True)
        if not item_types:
            subcategories = subcategories.filter(available=True)
        else:
            subcategories = subcategories.filter(item_type__in=item_types)
        if public:
            subcategories = subcategories.filter(submission=True)
        selected_cats = []
        if area_name:
            area = Area.objects.get(urn=area_name)
            # if there some restrictions with categories limit them
            if area.subcategories.count():
                sub_ids = [sub.id for sub in area.subcategories.all()]
                subcategories = subcategories.filter(id__in=sub_ids)
            selected_cats = [subcat.pk
                             for subcat in area.default_subcategories.all()]
        for sub_category in subcategories.order_by('order'):
            if sub_category.category not in sub_categories:
                sub_categories[sub_category.category] = []
            if sub_category.id in selected_cats:
                sub_category.selected = True
                sub_category.category.selected = True
            sub_categories[sub_category.category].append(sub_category)

        subcategories = [(cat, subcats) \
                           for cat, subcats in sub_categories.items()]
        get_cat_order = lambda cat_tuple: cat_tuple[0].order
        subcategories = sorted(subcategories, key=get_cat_order)
        return subcategories

IMPORTERS = {'KML':KMLManager,
             'OSM':OSMManager,
             'SHP':ShapefileManager,
             'RSS':GeoRSSManager,
             'CSV':CSVManager
             }

IMPORTER_CHOICES = (('KML', 'KML'),
                    ('OSM', 'OSM'),
                    ('SHP', 'Shapefile'),
                    ('RSS', 'GeoRSS'),
                    ('CSV', 'CSV')
                    )

IMPORTER_CHOICES_DICT = dict(IMPORTER_CHOICES)

class Importer(models.Model):
    '''
    Data importer for a specific subcategory
    '''
    importer_type = models.CharField(_(u"Importer type"), max_length=4,
                                     choices=IMPORTER_CHOICES)
    filtr = models.CharField(_(u"Filter"), max_length=200,
                             blank=True, null=True)
    source = models.CharField(_(u"Web address"), max_length=200,
                              blank=True, null=True)
    source_file = models.FileField(_(u"Source file"),
                        upload_to='import_files', blank=True, null=True)
    default_name = models.CharField(_(u"Name by default"), max_length=200,
                                    blank=True, null=True)
    srid = models.IntegerField(_(u"SRID"), blank=True, null=True)
    zipped = models.BooleanField(_(u"Zipped file"), default=False)
    overwrite = models.BooleanField(_(u"Overwrite existing data"),
                                    default=False)
    origin = models.CharField(_(u"Origin"), max_length=100,
                              blank=True, null=True)
    license = models.CharField(_(u"License"), max_length=100,
                               blank=True, null=True)
    categories = SelectMultipleField(SubCategory,
                      verbose_name=_(u"Associated subcategories"))
    state = models.CharField(_(u"State"), max_length=200,
                             blank=True, null=True)
    associate_marker_to_way = models.BooleanField(_(u"Automatically associate "\
                                           u"a marker to a way"), default=False)

    class Meta:
        verbose_name = _(u"Importer")

    def __unicode__(self):
        vals = [IMPORTER_CHOICES_DICT[self.importer_type],
                self.source, self.source_file.name,
                u", ".join([unicode(cat) for cat in self.categories.all()]),
                self.default_name]
        return u' %d: %s' % (self.pk, u" - ".join([unicode(v)
                                                   for v in vals if v]))

    @property
    def manager(self):
        return IMPORTERS[self.importer_type](self)

    def display_categories(self):
        return u"\n".join([cat.name for cat in self.categories.all()])

class GeographicItem(models.Model):
    name = models.CharField(_(u"Name"), max_length=150)
    categories = SelectMultipleField(SubCategory)
    submiter_session_key = models.CharField(_(u"Submitter session key"),
                                        blank=True, null=True, max_length=40)
    submiter_name = models.CharField(_(u"Submitter name or nickname"),
                                     blank=True, null=True, max_length=40)
    submiter_email = models.EmailField(_(u"Submitter email"), blank=True,
                                       null=True)
    submiter_comment = models.TextField(_(u"Submitter comment"), max_length=200,
                                        blank=True, null=True)
    STATUS = (('S', _(u'Submited')),
              ('A', _(u'Available')),
              ('M', _(u'Modified')),
              ('D', _(u'Disabled')),
              ('I', _(u'Imported')))
    STATUS_DCT = dict(STATUS)
    status = models.CharField(_(u"Status"), max_length=1, choices=STATUS)
    import_key = models.CharField(_(u"Import key"), max_length=200,
                                  blank=True, null=True)
    import_version = models.IntegerField(_(u"Import version"),
                                         blank=True, null=True)
    import_source = models.CharField(_(u"Source"), max_length=200,
                                     blank=True, null=True)
    modified_since_import = models.BooleanField(_(u"Modified since last import"),
                                                default=True)
    not_for_osm = models.BooleanField(_(u"Not to be exported to OSM"),
                                      default=False)
    origin = models.CharField(_(u"Origin"), max_length=100,
                              blank=True, null=True)
    license = models.CharField(_(u"License"), max_length=100,
                               blank=True, null=True)
    start_date = models.DateField(_(u"Start date"), blank=True, null=True,
        help_text=_(u"Not mandatory. Set it for dated item such as event. "\
                    u"Format YYYY-MM-DD"))
    end_date = models.DateField(_(u"End date"), blank=True, null=True,
        help_text=_(u"Not mandatory. Set it only if you have a multi-day "\
                    u"event. Format YYYY-MM-DD"))
    class Meta:
        abstract = True

    def get_key(self, key):
        key_vals = self.import_key.split(';')
        for k_v in key_vals:
            if k_v.startswith(key+':'):
                return k_v.split(':')[1]

    def set_key(self, key, value):
        new_keys, _set = '', None
        key_vals = self.import_key.split(';') if self.import_key else []
        for k_v in key_vals:
            if ':' not in k_v:
                continue
            k, v = k_v.split(':')
            if k == key:
                _set = True
                new_keys += '%s:%s;' % (k, value)
            else:
                new_keys += '%s:%s;' % (k, v)
        if not _set:
            new_keys += '%s:%s;' % (key, value)
        self.import_key = new_keys
        self.save()

    @classmethod
    def properties(cls):
        return [pm for pm in PropertyModel.objects.filter(available=True)]

def property_setter(cls, propertymodel):
    def setter(self, value):
        marker = self
        if cls == Route:
            if not self.associated_marker.objects.count():
                return
            marker = self.associated_marker.objects.all()[0]
        marker.setProperty(propertymodel, value)
    return setter

class Marker(GeographicItem):
    '''Marker for a POI
    '''
    ref_item = models.ForeignKey("Marker", blank=True, null=True,
            verbose_name=_(u"Reference marker"), related_name='submited_marker')
    point = PointField(_(u"Localisation"),
                       srid=settings.CHIMERE_EPSG_DISPLAY_PROJECTION)
    available_date = models.DateTimeField(_(u"Available Date"), blank=True,
                                          null=True) # used by feeds
    route = models.ForeignKey(u"Route", blank=True, null=True,
                              related_name='associated_marker')
    description = models.TextField(_(u"Description"), blank=True, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Marker, self).__init__(*args, **kwargs)
        # add read attributes for properties
        for pm in self.properties():
            attr_name = pm.getAttrName()
            if not hasattr(self, attr_name):
                val = ''
                property = self.getProperty(pm)
                if property:
                    val = property.python_value
                setattr(self, attr_name, val)
            if not hasattr(self, attr_name + '_set'):
                setattr(self, attr_name + '_set',
                              property_setter(self.__class__, pm))

    def get_init_multi(self):
        multis = [forms.model_to_dict(multi)
                  for multi in self.multimedia_files.all()]
        return multis

    def get_init_picture(self):
        picts = [forms.model_to_dict(pict)
                 for pict in self.pictures.all()]
        return picts

    @property
    def multimedia_items(self):
        pict = list(self.pictures.filter(miniature=False).all())
        mm = list(self.multimedia_files.filter(miniature=False).all())
        items = [(item.order, item) for item in pict + mm]
        return [item for order, item in sorted(items)]

    @property
    def default_pictures(self):
        return list(self.pictures.filter(miniature=True).order_by('order'))

    @property
    def default_multimedia_items(self):
        return list(self.multimedia_files.filter(miniature=True
                                                 ).order_by('order'))

    @property
    def date(self):
        if settings.CHIMERE_DAYS_BEFORE_EVENT:
            return self.start_date

    @property
    def geometry(self):
        return self.point.wkt

    @property
    def geom_attr(self):
        return 'point'

    class Meta:
        ordering = ('status', 'name')
        verbose_name = _(u"Point of interest")

    def getLatitude(self):
        '''Return the latitude
        '''
        return self.point.y

    def getLongitude(self):
        '''Return the longitude
        '''
        return self.point.x

    def getProperty(self, propertymodel, safe=None):
        """Get the property of an associated property model.
        If safe set to True, verify if the property is available
        """
        if safe and not propertymodel.available:
            return
        try:
            property = Property.objects.get(propertymodel=propertymodel,
                                            marker=self)
        except Property.DoesNotExist:
            return
        return property

    def getProperties(self):
        """Get all the property availables
        """
        properties = []
        for pm in PropertyModel.objects.filter(available=True):
            property = self.getProperty(pm)
            if property:
                properties.append(property)
        return properties

    def setProperty(self, pm, value):
        u"""
        Set a property
        """
        properties = Property.objects.filter(marker=self,
                                             propertymodel=pm).all()
        # in case of multiple edition as the same time delete arbitrary
        # the others
        if len(properties) > 1:
            for property in properties[1:]:
                property.delete()
        # new property
        if not properties:
            new_property = Property.objects.create(marker=self,
                                propertymodel=pm,
                                value=value)
            new_property.save()
        else:
            property = properties[0]
            property.value = value
            property.save()

    def saveProperties(self, values):
        """
        Save properties
        """
        for propertymodel in PropertyModel.objects.filter(available=True):
            val = u""
            if unicode(propertymodel.id) in values:
                val = values[unicode(propertymodel.id)]
            self.setProperty(propertymodel, val)

    def getGeoJSON(self, categories_id=[]):
        '''Return a GeoJSON string
        '''
        jsons = []
        for cat in self.categories.all():
            if categories_id and cat.id not in categories_id:
                continue
            items = {'id':self.id, 'name':json.dumps(self.name),
                     'geometry':self.point.geojson,
                     'icon_path':cat.icon.image,
                     'icon_width':cat.icon.image.width,
                     'icon_height':cat.icon.image.height,}
            jsons.append(u'{"type":"Feature", "geometry":%(geometry)s, '\
                u'"properties":{"pk": %(id)d, "name": %(name)s, '\
                u'"icon_path":"%(icon_path)s", "icon_width":%(icon_width)d, '\
                u'"icon_height":%(icon_height)d}}' % items)
        return ",".join(jsons)

    @property
    def default_category(self):
        # Should we select only available ones ?
        # Should we catch if not exists ?
        return self.categories.all()[0]

    def get_absolute_url(self, area_name=''):
        parameters = 'current_feature=%d&checked_categories=%s' % (self.id,
                                                    self.default_category.pk)
        urn = TinyUrl.getUrnByParameters(parameters)
        area_name = area_name + '/' if area_name else ''
        url = reverse('chimere:tiny', args=[area_name, urn])
        return url


PRE_ATTRS = {
    'Marker':('name', 'geometry', 'import_version', 'modified_since_import'),
    'Route':('name', 'geometry', 'import_version', 'modified_since_import'),
    'Area':('urn', 'name'),
    }
def geometry_pre_save(cls, pre_save_geom_values):
    def geom_pre_save(sender, **kwargs):
        if not kwargs['instance'] or not kwargs['instance'].pk:
            return
        instance = kwargs['instance']
        try:
            instance = cls.objects.get(pk=instance.pk)
            pre_save_geom_values[instance.pk] = [getattr(instance, attr)
                                            for attr in PRE_ATTRS[cls.__name__]]
        except ObjectDoesNotExist:
            pass
    return geom_pre_save

pre_save_marker_values = {}
def marker_pre_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    geometry_pre_save(Marker, pre_save_marker_values)(sender, **kwargs)
pre_save.connect(marker_pre_save, sender=Marker)

def geometry_post_save(pre_save_geom_values):
    def geom_post_save(sender, **kwargs):
        if not kwargs['instance'] \
           or kwargs['instance'].pk not in pre_save_geom_values:
            return
        instance = kwargs['instance']
        name, geometry, import_version, modified_since_import = \
                                    pre_save_geom_values[instance.pk]
        # force the reinit of modified_since_import
        if modified_since_import != instance.modified_since_import:
            return
        if (instance.import_version != import_version
           and instance.modified_since_import):
            instance.modified_since_import = False
            instance.save()
            return
        if instance.modified_since_import:
            return
        if instance.name != name or instance.geometry != geometry:
            instance.modified_since_import = True
            instance.save()
    return geom_post_save
def marker_post_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    geometry_post_save(pre_save_marker_values)(sender, **kwargs)
post_save.connect(marker_post_save, sender=Marker)

class MultimediaType(models.Model):
    MEDIA_TYPES = (('A', _(u"Audio")),
                   ('V', _(u"Video")),
                   ('I', _(u"Image")),
                   ('O', _(u"Other")),)
    media_type = models.CharField(_(u"Media type"), max_length=1,
                                  choices=MEDIA_TYPES)
    name = models.CharField(_(u"Name"), max_length=150)
    mime_type = models.CharField(_(u"Mime type"), max_length=50, blank=True,
                                 null=True)
    iframe = models.BooleanField(_(u"Inside an iframe"), default=False)
    available = models.BooleanField(_(u"Available"), default=True)

    class Meta:
        verbose_name = _(u"Multimedia type")
        verbose_name_plural = _(u"Multimedia types")

    def __unicode__(self):
        return self.name

    @classmethod
    def get_tuples(cls):
        vals = cls.objects.filter(available=True).order_by('media_type',
                                                           'name')
        tuples, c_tpe = [('', _("Automatic recognition"))], None
        media_type_dct = dict(cls.MEDIA_TYPES)
        for tpe, pk, name in [(media_type_dct[v.media_type], v.pk, v.name)
                              for v in vals]:
            if not c_tpe or c_tpe != tpe:
                c_tpe = tpe
                tuples.append([tpe, []])
            tuples[-1][1].append((pk, name))
        return tuples

IFRAME_LINKS = {
    'youtube':((re.compile(r'youtube.com\/watch\?v=([A-Za-z0-9_-]*)'),
                re.compile(r'youtu.be\/([A-Za-z0-9_-]*)'),
                re.compile(r'youtube.com\/embed\/([A-Za-z0-9_-]*)')),
                 "http://www.youtube.com/embed/%s"),
    'dailymotion':(
        (re.compile(r'dailymotion.com/video/([A-Za-z0-9]*)_[A-Za-z0-9_-]*'),
         re.compile(r'dailymotion.com/embed/video/([A-Za-z0-9]*)'),
         re.compile("http://www.dailymotion.com/embed/video/%s")),
         'http://www.dailymotion.com/embed/video/%s'),
    'vimeo':((re.compile(r'vimeo.com/video/([A-Za-z0-9]*)'),
              re.compile(r'vimeo.com/([A-Za-z0-9]*)'),),
              "http://player.vimeo.com/video/%s")
}

class MultimediaExtension(models.Model):
    name = models.CharField(_(u"Extension name"), max_length=6)
    multimedia_type = models.ForeignKey(MultimediaType,
                        verbose_name=_(u"Associated multimedia type"),
                        related_name='extensions')

    class Meta:
        verbose_name = _(u"Multimedia extension")
        verbose_name_plural = _(u"Multimedia extensions")

    def __unicode__(self):
        return self.name

class MultimediaFile(models.Model):
    name = models.CharField(_(u"Name"), max_length=150)
    url = models.URLField(_(u"Url"), max_length=200)
    order = models.IntegerField(_(u"Order"), default=1)
    multimedia_type = models.ForeignKey(MultimediaType, blank=True, null=True)
    miniature = models.BooleanField(_(u"Display inside the description?"),
                                  default=settings.CHIMERE_MINIATURE_BY_DEFAULT)
    marker = models.ForeignKey(Marker, related_name='multimedia_files')

    class Meta:
        verbose_name = _(u"Multimedia file")
        verbose_name_plural = _(u"Multimedia files")

    def __unicode__(self):
        return self.name or u""

def multimediafile_post_save(sender, **kwargs):
    if not kwargs['instance'] or not kwargs['created']:
        return
    multimediafile = kwargs['instance']
    # auto recognition of file types
    if not multimediafile.multimedia_type:
        url = multimediafile.url
        for mm_type in IFRAME_LINKS:
            res, embeded_url = IFRAME_LINKS[mm_type]
            if [r for r in res if r.search(url)]:
                multimedia_type = MultimediaType.objects.get(
                                    name__iexact=mm_type)
                multimediafile.multimedia_type = multimedia_type
        if not multimediafile.multimedia_type:
            ext = url.split(".")[-1]
            q = MultimediaExtension.objects.filter(name__iendswith=ext)
            if q.count():
                multimediafile.multimedia_type = q.all()[0].multimedia_type
            else:
                # default to an iframe
                multimediafile.multimedia_type = \
                   MultimediaType.objects.filter(name__iexact='iframe').all()[0]
    # manage iframe of video providers
    if multimediafile.multimedia_type.name.lower() in IFRAME_LINKS:
        regexps, lnk = IFRAME_LINKS[multimediafile.multimedia_type.name.lower()]
        key = None
        for regexp in regexps:
            key = regexp.findall(multimediafile.url)
            if key:
                key = key[0]
                break
        if key:
            multimediafile.url = lnk % key

    mfs = MultimediaFile.objects.filter(marker=multimediafile.marker).exclude(
                                        pk=multimediafile.pk).order_by('order')
    for idx, mf in enumerate(mfs.all()):
        mf.order = idx + 1
        mf.save()
    multimediafile.order = mfs.count() + 1
    multimediafile.save()
post_save.connect(multimediafile_post_save, sender=MultimediaFile)

class PictureFile(models.Model):
    name = models.CharField(_(u"Name"), max_length=150)
    picture = models.ImageField(_(u"Image"), upload_to='pictures',
                                height_field='height', width_field='width')
    height = models.IntegerField(_(u"Height"), blank=True, null=True)
    width = models.IntegerField(_(u"Width"), blank=True, null=True)
    miniature = models.BooleanField(_(u"Display inside the description?"),
                                  default=settings.CHIMERE_MINIATURE_BY_DEFAULT)
    thumbnailfile = models.ImageField(_(u"Thumbnail"), upload_to='pictures',
                        blank=True, null=True,
                        height_field='thumbnailfile_height',
                        width_field='thumbnailfile_width')
    thumbnailfile_height = models.IntegerField(_(u"Thumbnail height"),
                                               blank=True, null=True)
    thumbnailfile_width = models.IntegerField(_(u"Thumbnail width"),
                                              blank=True, null=True)
    order = models.IntegerField(_(u"Order"), default=1)
    marker = models.ForeignKey(Marker, related_name='pictures')

    def __unicode__(self):
        return self.name or u""

    class Meta:
        verbose_name = _(u"Picture file")
        verbose_name_plural = _(u"Picture files")

def scale_image(max_x, pair):
    x, y = pair
    new_y = (float(max_x) / x) * y
    return (int(max_x), int(new_y))

IMAGE_EXIF_ORIENTATION_MAP = {
    1: 0,
    8: 2,
    3: 3,
    6: 4,
}

PYEXIV2_OLD_API = not hasattr(pyexiv2, 'ImageMetadata')

def picturefile_post_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    picturefile = kwargs['instance']

    if kwargs['created']:
        filename = picturefile.picture.path
        metadata, orientation = None, None
        if PYEXIV2_OLD_API:
            metadata = pyexiv2.Image(filename)
            metadata.readMetadata()
            orientation = metadata['Exif.Image.Orientation'] \
                   if 'Exif.Image.Orientation' in metadata.exifKeys() else None
        else:
            metadata = pyexiv2.ImageMetadata(filename)
            metadata.read()
            orientation = metadata['Exif.Image.Orientation'].value \
                      if 'Exif.Image.Orientation' in metadata else None
        if orientation and orientation in IMAGE_EXIF_ORIENTATION_MAP \
           and orientation > 1:
            metadata['Exif.Image.Orientation'] = 1
            if PYEXIV2_OLD_API:
                metadata.writeMetadata()
            else:
                metadata.write()
            im = Image.open(filename)
            im = im.transpose(IMAGE_EXIF_ORIENTATION_MAP[orientation])
            im.save(filename)

    if not picturefile.thumbnailfile:
        file = picturefile.picture
        # defining the filename and the thumbnail filename
        filehead, filetail = os.path.split(os.path.abspath(file.path))
        basename, format = os.path.splitext(filetail)
        basename = defaultfilters.slugify(basename)
        basename = re.sub(r'-','_', basename)
        miniature = basename + '_thumb' + format
        filename = file.path
        miniature_filename = os.path.join(filehead, miniature)
        try:
            image = Image.open(filename)
        except:
            image = None
        if image:
            image_x, image_y = image.size
            if settings.CHIMERE_THUMBS_SCALE_HEIGHT:
                image_y, image_x = scale_image(
                                          settings.CHIMERE_THUMBS_SCALE_HEIGHT,
                                          (image_y, image_x))
            elif settings.CHIMERE_THUMBS_SCALE_WIDTH:
                image_x, image_y = scale_image(
                                          settings.CHIMERE_THUMBS_SCALE_WIDTH,
                                          (image_x, image_y))
            image.thumbnail([image_x, image_y], Image.ANTIALIAS)

            temp_image = open(miniature_filename, 'w')
            try:
                image.save(temp_image, image.format, quality=90, optimize=1)
            except:
                image.save(temp_image, image.format, quality=90)

            short_name = miniature_filename[len(settings.MEDIA_ROOT):]
            picturefile.thumbnailfile = short_name
            picturefile.save()

    if not kwargs['created']:
        return
    pfs = PictureFile.objects.filter(marker=picturefile.marker).exclude(
                                     pk=picturefile.pk).order_by('order')
    for idx, pf in enumerate(pfs.all()):
        pf.order = idx + 1
        pf.save()
    picturefile.order = pfs.count() + 1
    picturefile.save()
post_save.connect(picturefile_post_save, sender=PictureFile)

class RouteFile(models.Model):
    name = models.CharField(_(u"Name"), max_length=150)
    raw_file = models.FileField(_(u"Raw file (gpx or kml)"),
                                upload_to='route_files')
    simplified_file = models.FileField(_(u"Simplified file"),
                        upload_to='route_files', blank=True, null=True)
    TYPE = (('K', _(u'KML')), ('G', _(u'GPX')))
    file_type = models.CharField(max_length=1, choices=TYPE)

    class Meta:
        ordering = ('name',)
        verbose_name = _(u"Route file")
        verbose_name_plural = _(u"Route files")

    def __unicode__(self):
        return self.name

    def process(self):
        if self.simplified_file:
            return
        input_name = settings.MEDIA_ROOT + self.raw_file.name
        output_name = settings.MEDIA_ROOT + self.raw_file.name[:-4] + \
                      "_simplified" + ".gpx"
        cli_args = [settings.GPSBABEL, '-i']
        if self.file_type == 'K':
            cli_args.append('kml')
        elif self.file_type == 'G':
            cli_args.append('gpx')
        cli_args += ['-f', input_name, '-x', settings.GPSBABEL_OPTIONS,
                     '-o', 'gpx', '-F', output_name]
        p = Popen(cli_args, stderr=PIPE)
        p.wait()
        if p.returncode:
            print p.stderr.read()
            #logger.error(p.stderr.read())
        else:
            self.simplified_file = File(open(output_name))
            self.save()
            os.remove(output_name)

    @property
    def route(self):
        if not self.simplified_file:
            return

        file_name = settings.MEDIA_ROOT + self.simplified_file.name
        tree = etree.parse(file_name)
        pts = []
        for pt in tree.getiterator():
            if not pt.tag.endswith('trkpt'):
                continue
            pts.append((pt.get("lon"), pt.get("lat")))
        geojson_tpl = u'{"type":"Feature", "geometry":{ "type": "LineString", '\
                       '"coordinates":[%s]}}'
        wkt_tpl = u'LINESTRING(%s)'
        return wkt_tpl % u','.join([u'%s %s' % (pt[0], pt[1]) \
                                           for pt in pts])

class Route(GeographicItem):
    '''Route on the map
    '''
    ref_item = models.ForeignKey("Route", blank=True, null=True,
              verbose_name=_(u"Reference route"), related_name='submited_route')
    route = RouteField(_(u"Route"),
                       srid=settings.CHIMERE_EPSG_DISPLAY_PROJECTION)
    associated_file = models.ForeignKey(RouteFile, blank=True, null=True,
                                        verbose_name=_(u"Associated file"))
    picture = models.ImageField(_(u"Image"), upload_to='upload', blank=True,
                          null=True, height_field='height', width_field='width')
    height = models.IntegerField(_(u"Height"), blank=True, null=True)
    width = models.IntegerField(_(u"Width"), blank=True, null=True)
    has_associated_marker = models.BooleanField(_(u"Has an associated marker"),
                                                default=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('status', 'name')
        verbose_name = _(u"Route")

    def __init__(self, *args, **kwargs):
        super(Route, self).__init__(*args, **kwargs)
        self.description = ''
        try:
            associated_marker = Marker.objects.get(route=self)
            self.description = associated_marker.description
        except:
            associated_marker = None
        # add read attributes for properties
        for pm in self.properties():
            attr_name = pm.getAttrName()
            if not hasattr(self, attr_name):
                val = ''
                if associated_marker:
                    property = associated_marker.getProperty(pm)
                    if property:
                        val = property.python_value
                setattr(self, attr_name, val)
            if not hasattr(self, attr_name + '_set'):
                setattr(self, attr_name + '_set',
                              property_setter(self.__class__, pm))

    @property
    def geometry(self):
        return self.route.wkt

    @property
    def geom_attr(self):
        return 'route'

    def get_init_multi(self):
        if not self.associated_marker.count():
            return []
        multis = [forms.model_to_dict(multi)
            for multi in self.associated_marker.all()[0].multimedia_files.all()]
        return multis

    def get_init_picture(self):
        if not self.associated_marker.count():
            return []
        picts = [forms.model_to_dict(pict)
                 for pict in self.associated_marker.all()[0].pictures.all()]
        return picts

    def getProperty(self, propertymodel, safe=None):
        """Get the property of an associated property model.
        If safe set to True, verify if the property is available
        """
        if safe and not propertymodel.available:
            return
        try:
            property = Property.objects.get(propertymodel=propertymodel,
                                            marker=self)
        except Property.DoesNotExist:
            return
        return property

    def getProperties(self):
        """Get all the property availables
        """
        properties = []
        for pm in PropertyModel.objects.filter(available=True):
            property = self.getProperty(pm)
            if property:
                properties.append(property)
        return properties

    def getGeoJSON(self, color="#000"):
        '''Return a GeoJSON string
        '''
        if '#' not in color:
            color = '#' + color
        attributes = {'id':self.id, 'name':json.dumps(self.name),
                      'color':color, 'geometry':self.route.geojson,}
        return u'{"type":"Feature", "geometry":%(geometry)s, '\
               u'"properties":{"pk": %(id)d, "name": %(name)s, '\
               u'"color":"%(color)s"}}' % attributes

    def getTinyUrl(self):
        parameters = 'current_feature=%d&checked_categories=%s' % (self.id,
                                                          self.categories[0].id)
        return TinyUrl.getUrnByParameters(parameters)

pre_save_route_values = {}
def route_pre_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    geometry_pre_save(Route, pre_save_route_values)(sender, **kwargs)
pre_save.connect(route_pre_save, sender=Route)

def route_post_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    geometry_post_save(pre_save_route_values)(sender, **kwargs)
    instance = kwargs['instance']

    # manage associated marker
    if instance.has_associated_marker:
        marker_fields = [f.attname for f in Marker._meta.fields]
        route_fields = [f.attname for f in Route._meta.fields]
        marker_dct = dict([(k, getattr(instance, k)) for k in marker_fields
                       if k in route_fields and k not in ('id', 'ref_item_id')])
        marker_dct['point'] = "SRID=%d;POINT(%f %f)" % (instance.route.srid,
                                  instance.route[0][0], instance.route[0][1])
        marker, created = Marker.objects.get_or_create(route=instance,
                                                       defaults=marker_dct)
        if not created:
            marker.status = instance.status
            marker.point = marker_dct['point']
        marker.save()
        properties = {}
        for pm in instance.properties():
            prop = instance.getProperty(pm)
            if prop:
                properties[pm.pk] = prop.python_value
        # fix mis-initialized markers
        if created:
            for cat in instance.categories.all():
                marker.categories.add(cat)
        marker.saveProperties(properties)

post_save.connect(route_post_save, sender=Route)

def sync_m2m_route(sender, **kwargs):
    if kwargs['action'] not in ('post_add', 'post_clear', 'post_remove'):
        return
    route = kwargs['instance']
    marker = route.associated_marker
    if not marker.count():
        return
    marker = marker.all()[0]
    marker.categories.clear()
    if kwargs['action'] == 'post_clear':
        return
    for cat in route.categories.all():
        marker.categories.add(cat)
m2m_changed.connect(sync_m2m_route, sender=Route.categories.through)

def getDateCondition():
    '''
    Return an SQL condition for apparition of dates
    '''
    if not settings.CHIMERE_DAYS_BEFORE_EVENT:
        return ""
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    after = (datetime.datetime.now() + \
             datetime.timedelta(settings.CHIMERE_DAYS_BEFORE_EVENT)
                                                  ).strftime('%Y-%m-%d')
    date_condition = " and (%(alias)s.start_date is null or "
    date_condition += "(%(alias)s.start_date >= '" + now + "' and "
    date_condition += "%(alias)s.start_date <='" + after + "')"
    date_condition += " or (%(alias)s.start_date <='" + now + "' and "
    date_condition += "%(alias)s.end_date >='" + now + "')) "
    return date_condition

class SimplePoint:
    """
    Point in the map (not in the database)
    """
    def __init__(self, x, y):
        self.x, self.y = x, y

class SimpleArea:
    """
    Rectangular area of a map (not in the database)
    """
    def __init__(self, area):
        """
        Defining upper left corner ans lower right corner from a tuple
        """
        assert len(area) == 4
        x1, y1, x2, y2 = area
        self.upper_left_corner = SimplePoint(x1, y1)
        self.lower_right_corner = SimplePoint(x2, y2)

    def isIn(self, area):
        """
        Verify if the current area is in the designated area
        """
        if self.upper_left_corner.x >= area.upper_left_corner.x and \
           self.upper_left_corner.y <= area.upper_left_corner.x and \
           self.lower_right_corner.x <= area.lower_right_corner.x and \
           self.lower_right_corner.y >= area.lower_right_corner.y:
            return True
        return False

    def getCategories(self, status='A', filter_available=True, area_name=None):
        """
        Get categories for this area
        """
        wheres = []
        if area_name:
            subcategory_pks = []
            for cat, subcats in SubCategory.getAvailable(area_name=area_name):
                for subcat in subcats:
                    subcategory_pks.append(unicode(subcat.pk))
            if filter_available:
                wheres += ['subcat.available = TRUE',  'cat.available = TRUE']
            wheres += ['subcat.id in (%s)' % ",".join(subcategory_pks)]
        where = " where " + " and ".join(wheres) if wheres else ""

        equal_status = ''
        if len(status) == 1:
            equal_status = "='%s'" % status[0]
        elif status:
            equal_status = " in ('%s')" % "','".join(status)
        area = u"ST_GeometryFromText('POLYGON((%f %f,%f %f,%f %f,%f %f, %f %f"\
              u"))', %d)" % (self.upper_left_corner.x, self.upper_left_corner.y,
                          self.lower_right_corner.x, self.upper_left_corner.y,
                          self.lower_right_corner.x, self.lower_right_corner.y,
                          self.upper_left_corner.x, self.lower_right_corner.y,
                          self.upper_left_corner.x, self.upper_left_corner.y,
                          settings.CHIMERE_EPSG_DISPLAY_PROJECTION
                          )
        date_condition = getDateCondition()
        sql_main = '''select subcat.id as id, subcat.category_id as category_id,
        subcat.name as name, subcat.available as available,
        subcat.icon_id as icon_id, subcat.color_theme_id as color_theme_id,
        subcat.order as order, subcat.item_type as item_type
        from chimere_subcategory subcat
        inner join chimere_category cat on cat.id=subcat.category_id'''
        sql = sql_main + '''
        inner join chimere_marker mark on ST_Contains(%s, mark.point)''' % area
        if equal_status:
            sql += ' and mark.status' + equal_status
        sql += date_condition % {'alias':'mark'}
        sql += '''
        inner join chimere_marker_categories mc on mc.subcategory_id=subcat.id and
        mc.marker_id=mark.id'''
        sql += where
        subcats = set(SubCategory.objects.raw(sql))
        sql = sql_main + '''
        inner join chimere_route rt on (ST_Intersects(%s, rt.route) or
        ST_Contains(%s, rt.route))''' % (area, area)
        if equal_status:
            sql += ' and rt.status' + equal_status
        sql += date_condition % {'alias':'rt'}
        sql += '''
        inner join chimere_route_categories rc on rc.subcategory_id=subcat.id and
        rc.route_id=rt.id'''
        sql += where
        # subcats.union(set(SubCategory.objects.raw(sql)))
        # set union behave strangely. Doing it manualy...
        for c in set(SubCategory.objects.raw(sql)):
            subcats.add(c)
        return subcats

class Layer(models.Model):
    name = models.CharField(_(u"Name"), max_length=150)
    layer_code = models.TextField(_(u"Layer code"), max_length=300)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Layer")

class Area(models.Model, SimpleArea):
    """Rectangular area of the map
    """
    name = models.CharField(_(u"Name"), max_length=150)
    urn = models.SlugField(_(u"Area urn"), max_length=50, blank=True,
                           unique=True)
    welcome_message = models.TextField(_(u"Welcome message"), blank=True,
                                       null=True)
    order = models.IntegerField(_(u"Order"), unique=True)
    available = models.BooleanField(_(u"Available"))
    upper_left_corner = models.PointField(_(u"Upper left corner"),
            default='POINT(0 0)', srid=settings.CHIMERE_EPSG_DISPLAY_PROJECTION)
    lower_right_corner = models.PointField(_(u"Lower right corner"),
            default='POINT(0 0)', srid=settings.CHIMERE_EPSG_DISPLAY_PROJECTION)
    default = models.NullBooleanField(_(u"Default area"),
                    help_text=_(u"Only one area is set by default"))
    layers = SelectMultipleField(Layer, related_name='areas',
                                 through='AreaLayers', blank=True)
    default_subcategories = SelectMultipleField(SubCategory, blank=True,
                           verbose_name=_(u"Sub-categories checked by default"))
    dynamic_categories = models.NullBooleanField(
        _(u"Sub-categories dynamicaly displayed"),
        help_text=_(u"If checked, categories are only displayed in the menu if "
                    u"they are available on the current extent."))
    subcategories = SelectMultipleField(SubCategory, related_name='areas',
       blank=True, db_table='chimere_subcategory_areas',
       verbose_name=_(u"Restricted to theses sub-categories"),
       help_text=_(u"If no sub-category is set all sub-categories are "
                   u"available"))
    external_css = models.URLField(_(u"Link to an external CSS"), blank=True,
                                   null=True)
    restrict_to_extent = models.BooleanField(_(u"Restrict to the area extent"),
                                             default=False)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('order', 'name')
        verbose_name = _("Area")

    @classmethod
    def getAvailable(cls):
        '''Get available areas
        '''
        return cls.objects.filter(available=True)

    def getWkt(self):
        return "SRID=%d;POLYGON((%f %f,%f %f,%f %f,%f %f, %f %f))" % (
          settings.CHIMERE_EPSG_DISPLAY_PROJECTION,
          self.upper_left_corner.x, self.upper_left_corner.y,
          self.lower_right_corner.x, self.upper_left_corner.y,
          self.lower_right_corner.x, self.lower_right_corner.y,
          self.upper_left_corner.x, self.lower_right_corner.y,
          self.upper_left_corner.x, self.upper_left_corner.y,
          )

    def getIncludeMarker(self):
        """
        Get the sql statement for the test if the point is included in the area
        """
        return Q(point__contained=self.getWkt())

    def getIncludeRoute(self):
        """
        Get the sql statement for the test if the route is included in the area
        """
        return Q(route__contained=self.getWkt())

pre_save_area_values = {}
def area_pre_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    geometry_pre_save(Area, pre_save_area_values)(sender, **kwargs)
pre_save.connect(area_pre_save, sender=Area)

def area_post_save(sender, **kwargs):
    if not kwargs['instance']:
        return
    area = kwargs['instance']
    if area.default:
        defaults = Area.objects.filter(default=True).exclude(pk=area.pk)
        for default in defaults:
            default.default = False
            default.save()
    # manage permissions
    old_urn, old_name = area.urn, area.name
    if area.pk in pre_save_area_values:
        old_urn, old_name = pre_save_area_values[area.pk]
    perm, old_groups, old_users = None, [], []
    if area.urn != old_urn:
        oldmnemo = 'change_area_' + old_urn
        old_perm = Permission.objects.filter(codename=oldmnemo)
        if old_perm.count():
            perm = old_perm.all()[0]
            perm.codename = 'change_area_' + area.urn
            perm.save()
    if not area.urn:
        area.urn = defaultfilters.slugify(area.name)
        area.save()
    mnemo = 'change_area_' + area.urn
    perm = Permission.objects.filter(codename=mnemo)
    lbl = "Can change " + area.name
    if not perm.count():
        content_type = ContentType.objects.get(app_label="chimere",
                                               model="area")
        perm = Permission(name=lbl, content_type_id=content_type.id,
                          codename=mnemo)
        perm.save()
    else:
        perm = perm.all()[0]
        if old_name != area.name:
            perm.name = lbl
            perm.save()
    # manage moderation group
    groupname = area.name + " moderation"
    if old_name != area.name:
        old_groupname = old_name + " moderation"
        old_gp = Group.objects.filter(name=old_groupname)
        if old_gp.count():
            old_gp = old_gp.all()[0]
            old_gp.name = groupname
            old_gp.save()
    group = Group.objects.filter(name=groupname)
    if not group.count():
        group = Group.objects.create(name=groupname)
        group.permissions.add(perm)
        for app_label, model in (('chimere', 'marker'),
                                 ('chimere', 'route'),
                                 ('chimere', 'multimediafile'),
                                 ('chimere', 'picturefile'),
                                 ('chimere', 'routefile')):
            ct = ContentType.objects.get(app_label=app_label, model=model)
            for p in Permission.objects.filter(content_type=ct).all():
                group.permissions.add(p)

post_save.connect(area_post_save, sender=Area)

def get_areas_for_user(user):
    """
    Getting subcats for a specific user
    """
    perms = user.get_all_permissions()
    areas = set()
    prefix = 'chimere.change_area_'
    for perm in perms:
        if perm.startswith(prefix):
            try:
                area = Area.objects.get(urn=perm[len(prefix):])
                areas.add(area)
            except ObjectDoesNotExist:
                pass
    return areas

def get_users_by_area(area):
    if not area:
        return []
    perm = 'change_area_'+area.urn
    return User.objects.filter(Q(groups__permissions__codename=perm)|
                                Q(user_permissions__codename=perm)).all()

class AreaLayers(models.Model):
    area = models.ForeignKey(Area)
    layer = models.ForeignKey(Layer)
    order = models.IntegerField(_(u"Order"))
    default = models.NullBooleanField(_(u"Default layer"))

    class Meta:
        ordering = ('order',)
        verbose_name = _("Layers")
        verbose_name_plural = _("Layers")

class PropertyModel(models.Model):
    '''Model for a property
    '''
    name = models.CharField(_(u"Name"), max_length=150)
    order = models.IntegerField(_(u"Order"))
    available = models.BooleanField(_(u"Available"))
    mandatory = models.BooleanField(_(u"Mandatory"))
    subcategories = SelectMultipleField(SubCategory, related_name='properties',
       blank=True, verbose_name=_(u"Restricted to theses sub-categories"),
       help_text=_(u"If no sub-category is set all the property applies to all "
                   u"sub-categories"))
    TYPE = (('T', _('Text')),
            ('L', _('Long text')),
            ('P', _('Password')),
            ('D', _("Date")))
    TYPE_WIDGET = {'T':forms.TextInput,
                   'L':TextareaWidget,
                   'P':forms.PasswordInput,
                   'D':DatePickerWidget}
    type = models.CharField(_(u"Type"), max_length=1, choices=TYPE)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ('order',)
        verbose_name = _("Property model")

    def getAttrName(self):
        attr_name = defaultfilters.slugify(self.name)
        attr_name = re.sub(r'-','_', attr_name)
        return attr_name

    def getNamedId(self):
        '''Get the name used as named id (easily sortable)
        '''
        return 'property_%d_%d' % (self.order, self.id)

class Property(models.Model):
    '''Property for a POI
    '''
    marker = models.ForeignKey(Marker, verbose_name=_(u"Point of interest"))
    propertymodel = models.ForeignKey(PropertyModel,
                                      verbose_name=_(u"Property model"))
    value = models.TextField(_(u"Value"))
    def __unicode__(self):
        return "%s : %s" % (str(self.propertymodel), self.value)
    class Meta:
        verbose_name = _(u"Property")

    @property
    def python_value(self):
        if self.propertymodel.type == 'D':
            try:
                return datetime.date(*[int(val) for val in self.value.split('-')])
            except:
                return ""
        else:
            return self.value

