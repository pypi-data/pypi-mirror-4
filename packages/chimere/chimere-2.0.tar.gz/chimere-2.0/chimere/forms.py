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
Forms
"""
from django import forms
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Permission, ContentType
from django.contrib.admin.widgets import AdminDateWidget
from django.core.mail import EmailMessage, BadHeaderError

from chimere.models import Marker, Route, PropertyModel, Property, Area,\
   News, Category, SubCategory, RouteFile, MultimediaFile, MultimediaType, \
   PictureFile, Importer, IMPORTER_CHOICES, IFRAME_LINKS, MultimediaExtension
from chimere.widgets import AreaField, PointField, TextareaWidget, \
    ImportFiltrWidget, TextareaAdminWidget, DatePickerWidget, \
    ImporterChoicesWidget, RE_XAPI

from datetime import timedelta, datetime, tzinfo

ZERO = timedelta(0)

class UTC(tzinfo):
    """UTC time zone"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return settings.TIME_ZONE

    def dst(self, dt):
        return ZERO

def notifyStaff(subject, body, sender=None):
    if not settings.EMAIL_HOST:
        return
    if settings.PROJECT_NAME:
        subject = u'[%s] %s' % (settings.PROJECT_NAME, subject)
    user_list = [u.email for u in
          User.objects.filter(is_staff=True).exclude(email="").order_by('id')]
    headers = {}
    if sender:
        headers['Reply-To'] = sender
    email = EmailMessage(subject, body, user_list[0], user_list,
                         headers=headers)
    try:
        email.send()
    except BadHeaderError:
        return False
    return True

def notifySubmission(absolute_uri, geo_object):
    category = u" - ".join([unicode(cat) for cat in geo_object.categories.all()])
    subject = u'%s %s' % (_(u"New submission for"), category)
    message = _(u'The new item "%s" has been submited in the category: ') % \
              geo_object.name + category
    message += "\n\n" + _(u"To valid, precise or unvalid this item: ")
    named_url = 'admin:chimere_%s_change'% geo_object.__class__.__name__.lower()
    message += absolute_uri + reverse(named_url, args=(geo_object.pk,))
    message += u"\n\n--\nChimère"
    return notifyStaff(subject, message)

class ContactForm(forms.Form):
    """
    Main form for categories
    """
    email = forms.EmailField(label=_("Email (optional)"), required=False)
    content = forms.CharField(label=_("Object"), widget=forms.Textarea)

class OSMForm(forms.Form):
    """
    OSM export form
    """
    username = forms.CharField(label=_("OSM user"))
    password = forms.CharField(label=_(u"Password"),
                               widget=forms.PasswordInput(render_value=False))
    # API URL are hardcoded: the day the API change Chimère will need
    # adaptations not only on this portion...
    api = forms.ChoiceField(label=_(u"API"),
            choices=(('', '--'),
                     ('api06.dev.openstreetmap.org',
                      _(u"Test API - %s") % 'api06.dev.openstreetmap.org'),
                     ('api.openstreetmap.org/api',
                      _(u"Main API - %s") % 'api.openstreetmap.org/api'),
                     ))

class NewsAdminForm(forms.ModelForm):
    """
    Main form for news
    """
    content = forms.CharField(widget=TextareaAdminWidget)
    class Meta:
        model = News

class ImporterAdminForm(forms.ModelForm):
    filtr = forms.CharField(widget=ImportFiltrWidget, required=False)
    importer_type = forms.ChoiceField(widget=ImporterChoicesWidget,
                                    choices=[('', '--')]+list(IMPORTER_CHOICES))
    class Meta:
        model = Importer
        widgets = {
            'source': forms.TextInput(attrs={'size': 80}),
            'filtr': forms.TextInput(attrs={'size': 80}),
        }

    def clean(self):
        '''
        Verify that only one type of source is provided
        Verify that shapefiles are zipped
        '''
        if self.cleaned_data.get('importer_type') == 'OSM' and \
           not self.cleaned_data.get('filtr'):
            raise forms.ValidationError(_(u"For OSM import you must be "\
                      u"provide a filter. Select an area and node/way filter."))
        if self.cleaned_data.get('importer_type') == 'OSM' and \
           not RE_XAPI.match(self.cleaned_data.get('filtr')):
            raise forms.ValidationError(_(u"For OSM import you must be "\
                      u"provide a filter. Select an area and node/way filter."))
        if self.cleaned_data.get('importer_type') == 'SHP' and \
           not self.cleaned_data.get('zipped'):
            raise forms.ValidationError(_(u"Shapefiles must be provided in a "\
                                          u"zipped archive."))
        if self.cleaned_data.get('source') and \
           self.cleaned_data.get('source_file'):
            raise forms.ValidationError(_(u"You have to set \"source\" or "
                                          u"\"source file\" but not both."))
        if not self.cleaned_data.get('source') and \
           not self.cleaned_data.get('source_file') and \
           self.cleaned_data.get('importer_type') != 'OSM':
            raise forms.ValidationError(_(u"You have to set \"source\" or "
                                          u"\"source file\"."))
        return self.cleaned_data

class CategoryAdminForm(forms.ModelForm):
    """
    Main form for categories
    """
    description = forms.CharField(widget=TextareaAdminWidget, required=False)
    class Media:
        js = list(settings.JQUERY_JS_URLS) + [
            '%schimere/js/menu-sort.js' % settings.STATIC_URL,
        ]
    class Meta:
        model = Category

class MarkerAdminFormBase(forms.ModelForm):
    """
    Main form for marker
    """
    description = forms.CharField(widget=TextareaAdminWidget, required=False)
    class Meta:
        model = Marker

    def __init__(self, *args, **keys):
        """
        Custom initialization method in order to manage properties
        """
        self.pms = [pm for pm in PropertyModel.objects.filter(available=True)]
        if 'instance' in keys and keys['instance']:
            instance = keys['instance']
            property_dct = {}
            for pm in self.pms:
                property  = instance.getProperty(pm)
                if property:
                    property_dct[pm.getNamedId()] = property.value
            if 'initial' in keys:
                keys['initial'].update(property_dct)
            else:
                keys['initial'] = property_dct
        subcategories = keys.pop('subcategories') \
                        if 'subcategories' in keys else []
        super(MarkerAdminFormBase, self).__init__(*args, **keys)
        if settings.CHIMERE_DAYS_BEFORE_EVENT:
            self.fields['start_date'].widget = DatePickerWidget()
            self.fields['end_date'].widget = DatePickerWidget()
        if subcategories:
            self.fields['categories'].choices = subcategories

    def clean(self):
        '''
        Verify that a start date is provided when an end date is set
        Verify the mandatory properties (to be check manualy because it depends
        on the checked categories)
        '''
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if end_date and not start_date:
            msg = _(u"End date has been set with no start date")
            self._errors["end_date"] = self.error_class([msg])
            del self.cleaned_data['end_date']
        if end_date and start_date and start_date > end_date:
            msg = _(u"End date can't be before start date")
            self._errors["end_date"] = self.error_class([msg])
            raise forms.ValidationError(msg)
        for pm in self.pms:
            if not pm.mandatory or self.cleaned_data[pm.getNamedId()]:
                continue
            pm_cats = pm.subcategories.all()
            if not pm_cats or \
               [submited_cat for submited_cat in self.cleaned_data['categories']
                             if submited_cat in pm_cats]:
                msg = _(u"This field is mandatory for the selected categories")
                self._errors[pm.getNamedId()] = self.error_class([msg])
                #raise forms.ValidationError()
        return self.cleaned_data

    def save(self, *args, **keys):
        """
        Custom save method in order to manage associated properties
        """
        new_marker = super(MarkerAdminFormBase, self).save(*args, **keys)
        if 'status' not in self.cleaned_data and not new_marker.status:
            new_marker.status = 'S'
        if new_marker.status == 'A':
            tz = UTC()
            new_marker.available_date = datetime.replace(datetime.utcnow(),
                                                         tzinfo=tz)
        new_marker.save()
        # save properties
        properties = dict([(k.split('_')[-1], self.cleaned_data[k]) \
                for k in self.cleaned_data.keys() if k.startswith('property_')])
        new_marker.saveProperties(properties)
        return new_marker

# As we have dynamic fields, it's cleaner to make the class dynamic too
fields = {}
# declare properties
for prop in PropertyModel.objects.filter(available=True):
    key = "property_%d_%d" % (prop.order, prop.id)
    fields[key] = forms.CharField(label=prop.name,
                                 widget=PropertyModel.TYPE_WIDGET[prop.type],
                                 required=False)
MarkerAdminForm = type("MarkerAdminForm", (MarkerAdminFormBase,), fields)

class MarkerForm(MarkerAdminForm):
    """
    Form for the edit page
    """
    ref_pk = forms.IntegerField(label=u" ", widget=forms.HiddenInput(),
                                required=False)
    description = forms.CharField(widget=TextareaWidget, required=False)
    class Meta:
        model = Marker
        exclude = ('status',)
        widgets = {
            'description': TextareaWidget(),
        }

class RouteAdminForm(forms.ModelForm):
    """
    Main form for route
    """
    class Meta:
        model = Route

    def __init__(self, *args, **keys):
        """
        Custom initialization method in order to manage properties
        """
        if 'instance' in keys and keys['instance']:
            instance = keys['instance']
            property_dct = {}
            for pm in PropertyModel.objects.filter(available=True):
                property  = instance.getProperty(pm)
                if property:
                    property_dct[pm.getNamedId()] = property.value
            if 'initial' in keys:
                keys['initial'].update(property_dct)
            else:
                keys['initial'] = property_dct
        subcategories = keys.pop('subcategories') \
                        if 'subcategories' in keys else []
        super(RouteAdminForm, self).__init__(*args, **keys)
        if settings.CHIMERE_DAYS_BEFORE_EVENT:
            self.fields['start_date'].widget = DatePickerWidget()
            self.fields['end_date'].widget = DatePickerWidget()
        if subcategories:
            self.fields['categories'].choices = subcategories

    def save(self, *args, **keys):
        """
        Custom save method in order to manage associated properties
        """
        new_route = super(RouteAdminForm, self).save(*args, **keys)
        if 'status' not in self.cleaned_data and not new_route.status:
            new_route.status = 'S'
        new_route.save()
        return new_route

class RouteForm(RouteAdminForm):
    """
    Form for the edit page
    """
    description = forms.CharField(widget=TextareaWidget, required=False)
    point = forms.CharField(label=" ", required=False, widget=forms.HiddenInput)
    associated_file_id = forms.CharField(label=" ", required=False,
                                   widget=forms.HiddenInput)
    class Meta:
        model = Route
        exclude = ('status',)

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            try:
                marker = Marker.objects.get(route=kwargs['instance'])
                kwargs['initial'] = {
                    'point':marker.point,
                    'description':marker.description}
                property_dct = {}
                for pm in PropertyModel.objects.filter(available=True):
                    property  = marker.getProperty(pm)
                    if property:
                        property_dct[pm.getNamedId()] = property.value
                if 'initial' in kwargs:
                    kwargs['initial'].update(property_dct)
                else:
                    kwargs['initial'] = property_dct
            except:
                pass
        super(RouteForm, self).__init__(*args, **kwargs)

    def save(self, *args, **keys):
        """
        Custom save method in order to manage associated marker and file
        """
        new_route = super(RouteForm, self).save(*args, **keys)
        if new_route.status == 'S':
            new_route.has_associated_marker = True
            new_route.save()
        # associate a route file
        if 'associated_file_id' in self.cleaned_data and \
           self.cleaned_data['associated_file_id']:
            file_pk = int(self.cleaned_data['associated_file_id'])
            new_route.associated_file = RouteFile.objects.get(pk=file_pk)
            new_route.save()
        # change the associated marker (if available)
        q_new_marker = Marker.objects.filter(route=new_route)
        if not q_new_marker.count():
            return new_route
        new_marker = q_new_marker.all()[0]
        # save description
        if self.cleaned_data['description']:
            new_marker.description = self.cleaned_data['description']
            new_marker.save()
        # save properties
        properties = dict([(k.split('_')[-1], self.cleaned_data[k]) \
                for k in self.cleaned_data.keys() if k.startswith('property_')])
        new_marker.saveProperties(properties)
        return new_route

class BaseFileForm(forms.ModelForm):
    id = forms.IntegerField(label=u"", widget=forms.HiddenInput(),
                            required=False)

    def __init__(self, *args, **kwargs):
        if not hasattr(self, '_related_name') or not self._related_name:
            raise ImproperlyConfigured
        super(BaseFileForm, self).__init__(*args, **kwargs)
        self.fields.pop('marker')

    def save(self, associated_marker):
        if not hasattr(self, 'cleaned_data') or not self.cleaned_data:
            return
        instance = None
        if self.cleaned_data.get('id'):
            try:
                instance = self._meta.model.objects.get(
                                    pk=self.cleaned_data['id'])
            except:
                pass
            self.cleaned_data.pop('id')
        if self.cleaned_data.get('DELETE'):
            if instance:
                instance.delete()
            return
        self.cleaned_data.pop('DELETE')
        self.cleaned_data['marker'] = associated_marker
        if instance:
            for k in self.cleaned_data:
                setattr(instance, k, self.cleaned_data[k])
            instance.save()
        else:
            instance = self._meta.model.objects.create(**self.cleaned_data)

class MultimediaFileAdminForm(forms.ModelForm):
    class Meta:
        model = MultimediaFile
    class Media:
        js = list(settings.JQUERY_JS_URLS) + [
            '%schimere/js/menu-sort.js' % settings.STATIC_URL,
        ]

    def __init__(self, *args, **kwargs):
        super(MultimediaFileAdminForm, self).__init__(*args, **kwargs)
        self.fields['multimedia_type'].widget.choices = \
                                                MultimediaType.get_tuples()

class MultimediaFileForm(BaseFileForm):
    """
    Form for a multimedia file
    """
    _related_name = 'multimedia_files'
    class Meta:
        model = MultimediaFile
        exclude = ('order',)

    def __init__(self, *args, **kwargs):
        super(MultimediaFileForm, self).__init__(*args, **kwargs)
        self.fields['multimedia_type'].widget.choices = \
                                                MultimediaType.get_tuples()
        # this can be auto detect
        self.fields['multimedia_type'].required = False

MultimediaFileFormSet = formset_factory(MultimediaFileForm, can_delete=True)

class PictureFileAdminForm(forms.ModelForm):
    class Meta:
        model = PictureFile
    class Media:
        js = list(settings.JQUERY_JS_URLS) + [
            '%schimere/js/menu-sort.js' % settings.STATIC_URL,
        ]

class PictureFileForm(BaseFileForm):
    """
    Form for a picture file
    """
    _related_name = 'pictures'
    class Meta:
        model = PictureFile
        exclude = ('order', 'height', 'width', 'thumbnailfile',
                   'thumbnailfile_height', 'thumbnailfile_width')

PictureFileFormSet = formset_factory(PictureFileForm, can_delete=True)

class FileForm(forms.Form):
    raw_file  = forms.FileField(label=_(u"File"))

    def clean_raw_file(self):
        data = self.cleaned_data['raw_file']
        if '.' not in data.name or \
           data.name.split('.')[-1].lower() not in ('kml', 'gpx'):
            raise forms.ValidationError(_(u"Bad file format: this must be a "\
                                          u"GPX or KML file"))
        return data

class FullFileForm(FileForm):
    name = forms.CharField(label=_(u"Name"), max_length=150)
    def __init__(self, *args, **kwargs):
        super(FullFileForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['name', 'raw_file']

class AreaAdminForm(forms.ModelForm):
    """
    Admin page to create an area
    """
    area = AreaField(label=_("Area"), fields=(PointField(), PointField()))
    welcome_message = forms.CharField(widget=TextareaAdminWidget,
                                      required=False)
    class Meta:
        model = Area

    def __init__(self, *args, **keys):
        """
        Custom initialization method in order to manage area
        """
        if args:
            vals = args[0]
            for k in ('upper_left_lat', 'upper_left_lon',
                      'lower_right_lat', 'lower_right_lon'):
                v = vals.get(k)
                try:
                    v = float(v)
                except ValueError:
                    v = None
                if not v:
                    args[0][k] = None
        if 'instance' in keys and keys['instance']:
            instance = keys['instance']
            dct = {'area':(instance.upper_left_corner,
                             instance.lower_right_corner)}
            if 'initial' in keys:
                keys['initial'].update(dct)
            else:
                keys['initial'] = dct
        super(AreaAdminForm, self).__init__(*args, **keys)

    def clean(self):
        '''
        Verify that the area is not empty
        '''
        if not self.cleaned_data.get('upper_left_lat') \
           and not self.cleaned_data.get('upper_left_lon') \
           and not self.cleaned_data.get('lower_right_lat') \
           and not self.cleaned_data.get('lower_right_lon') \
           and not self.cleaned_data.get('area'):
            msg = _(u"No area selected.")
            raise forms.ValidationError(msg)
        if self.cleaned_data.get('order'):
            q = Area.objects.filter(order=self.cleaned_data.get('order'))
            if self.instance:
                q = q.exclude(pk=self.instance.pk)
            if q.count():
                msg= _(u"The area \"%s\" has the same order, you need to "
                       u" choose another one.") % unicode(q.all()[0])
                raise forms.ValidationError(msg)
        return self.cleaned_data

    def save(self, *args, **keys):
        """
        Custom save method in order to manage area
        """
        new_area = super(AreaAdminForm, self).save(*args, **keys)
        area = self.cleaned_data['area']
        new_area.upper_left_corner = 'POINT(%s %s)' % (area[0][0], area[0][1])
        new_area.lower_right_corner = 'POINT(%s %s)' % (area[1][0],
                                                         area[1][1])
        content_type = ContentType.objects.get(app_label="chimere",
                                               model="area")
        if new_area.urn:
            mnemo = 'change_area_' + new_area.urn
            perm = Permission.objects.filter(codename=mnemo)
            if not perm:
                perm = Permission(name='Can change ' + new_area.name,
                           content_type_id=content_type.id, codename=mnemo)
                perm.save()
        else:
            if 'urn' in self.initial:
                mnemo = 'change_area_' + self.initial['urn']
                perm = Permission.objects.filter(codename=mnemo)
                if perm:
                    perm[0].delete()
        return new_area

class AreaForm(AreaAdminForm):
    """
    Form for the edit page
    """
    class Meta:
        model = Area

