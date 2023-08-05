#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008-2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>
#
# RSS : Copyright (C) 2010 Pierre Clarenc <pierre.crc_AT_gmailDOTcom>,
#                          Samuel Renard <renard.samuel_AT_gmailDOTcom>,

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
Views of the project
"""

import datetime
from itertools import groupby
import re

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import loader, RequestContext
from django.utils import simplejson
from django.utils.http import urlquote
from django.utils.translation import ugettext as _

from chimere.actions import actions
from chimere.models import Category, SubCategory, PropertyModel, \
     Marker, Route, News, SimpleArea, Area, Color, TinyUrl, RouteFile, \
     get_users_by_area

from chimere.widgets import getMapJS, PointChooserWidget, \
                            RouteChooserWidget, AreaWidget
from chimere.forms import MarkerForm, RouteForm, ContactForm, FileForm, \
     FullFileForm, MultimediaFileFormSet, PictureFileFormSet, notifySubmission,\
     notifyStaff, AreaForm

def get_base_uri(request):
    base_uri = 'http://'
    if 'HTTP_REFERER' in request.META:
        if request.META['HTTP_REFERER'].startswith('https:'):
            base_uri = 'https://'
    if 'SERVER_NAME' in request.META:
        base_uri += request.META['SERVER_NAME']
        if 'SERVER_PORT' in request.META and \
           str(request.META['SERVER_PORT']) != '80':
            base_uri += ":" + str(request.META['SERVER_PORT'])
    return base_uri

#TODO: convert to requestcontext
def get_base_response(area_name=""):
    """
    Get the base url
    """
    base_response_dct = {'media_path':settings.MEDIA_URL,}
    base_url = reverse("chimere:index")
    if not base_url.startswith('/'):
        base_url = '/' + base_url
    if area_name and area_name.endswith('/'):
        area_name = area_name[:-1]
    if area_name:
        base_response_dct['area_name_slash'] = area_name + "/"
        if base_url[-1] != '/':
            base_url += '/'
        base_url += area_name + '/'
    base_response_dct['extra_url'] = base_url
    area = None
    if area_name:
        try:
            area = Area.objects.get(urn=area_name, available=True)
        except ObjectDoesNotExist:
            return None, redirect(reverse('chimere:index'))
    else:
        try:
            area = Area.objects.get(default=True)
            area_name = area.urn
        except ObjectDoesNotExist:
            pass

    base_response_dct['area'] = area
    base_response_dct['area_name'] = area_name
    if area and area.external_css:
        base_response_dct['css_area'] = area.external_css
    base_response_dct['dynamic_categories'] = True \
            if area and area.dynamic_categories else False
    base_response_dct['JQUERY_JS_URLS'] = settings.JQUERY_JS_URLS
    base_response_dct['JQUERY_CSS_URLS'] = settings.JQUERY_CSS_URLS
    return base_response_dct, None

def index(request, area_name=None, default_area=None, simple=False):
    """
    Main page
    """
    # show the news
    # only if user is not came yet today
    today = datetime.date.today().strftime('%y-%m-%d')
    news_visible = False
    if not 'last_visit' in request.session or \
       request.session['last_visit'] != today:
        request.session['last_visit'] = today
        news_visible = True
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    # don't mess with permalink
    zoomout = True
    if request.GET and 'lat' in request.GET \
      and 'lon' in request.GET:
        zoomout = None
    response_dct.update({
         'actions':actions, 'action_selected':('view',),
         'error_message':'',
         'news_visible': news_visible,
         'areas_visible': settings.CHIMERE_DISPLAY_AREAS,
         'map_layer':settings.CHIMERE_DEFAULT_MAP_LAYER,
         'dynamic_categories':response_dct['dynamic_categories'],
         'zoomout':zoomout
        })
    tpl = 'chimere/main_map.html'
    if simple:
        tpl = 'chimere/main_map_simple.html'
    return render_to_response(tpl, response_dct,
                              context_instance=RequestContext(request))

def get_edit_page(redirect_url, item_cls, item_form,
                  multimediafile_formset=MultimediaFileFormSet,
                  picturefile_formset=PictureFileFormSet):
    """
    Edition page
    """
    def func(request, area_name="", item_id=None, cat_type=['M']):
        response_dct, redir = get_base_response(area_name)
        if redir:
            return redir, None, None
        if 'area_name' in response_dct:
            area_name = response_dct['area_name']
        subcategories = SubCategory.getAvailable(cat_type, area_name,
                                                 public=True)
        listed_subcats = []
        if subcategories:
            for cat, subcats in subcategories:
                listed_subcats.append((unicode(cat),
                         [(subcat.pk, subcat.name) for subcat in subcats]))
        # if an item_id is provided: modification
        init_item, ref_item = None, None
        if item_id:
            try:
                init_item = item_cls.objects.get(pk=item_id)
            except:
                return redirect(redirect_url, area_name + '/' if area_name \
                                else ''), None, None
            ref_item = init_item
            modified_item = item_cls.objects.filter(ref_item=init_item,
                               submiter_session_key=request.session.session_key)
            if modified_item.count():
                init_item = modified_item.all()[0]

        init_multi = init_item.get_init_multi() if init_item else None
        init_picture = init_item.get_init_picture() if init_item else None
        if init_item and not request.user.is_superuser and \
                         not init_item.submiter_session_key == \
                                        request.session.session_key:
            # hide personal information
            for k in ('submiter_name', 'submiter_email', 'submiter_comment'):
                setattr(init_item, k, '')
        # If the form has been submited
        if request.method == 'POST':
            inst = None
            # allow to directly modify only if owner or superuser
            if init_item and (request.user.is_superuser or \
                           init_item.submiter_session_key == \
                                        request.session.session_key):
                inst = init_item
            form = item_form(request.POST, request.FILES, instance=inst,
                             subcategories=listed_subcats)
            formset_multi = multimediafile_formset(request.POST, request.FILES,
                                        initial=init_multi, prefix='multimedia')
            formset_picture = picturefile_formset(request.POST, request.FILES,
                                        initial=init_picture, prefix='picture')
            # All validation rules pass
            if form.is_valid() and formset_multi.is_valid() and \
               formset_picture.is_valid():
                item = form.save()
                # set the session key (to permit modifications)
                item.submiter_session_key = request.session.session_key

                # associate to the reference item
                if ref_item:
                    item.ref_item = ref_item
                    if item.pk != ref_item.pk:
                        item.status = 'M'
                        if hasattr(ref_item, 'has_associated_marker'):
                            item.has_associated_marker = \
                                                ref_item.has_associated_marker
                elif not item.ref_item:
                    # initialisation
                    item.ref_item = item

                # just submited
                if not item.status:
                    item.status = 'S'
                item.save()

                marker = item
                if not isinstance(marker, Marker) \
                   and item.associated_marker.count():
                    marker = item.associated_marker.all()[0]
                if marker:
                    # manage multimedia items
                    for f in formset_multi:
                        f.save(marker)

                    for f in formset_picture:
                        f.save(marker)
                base_uri = get_base_uri(request)
                notifySubmission(base_uri, item)
                response_dct = get_base_response(area_name)
                return redirect(redirect_url + '-item',
                            area_name + '/' if area_name else '',
                            item.ref_item.pk, 'submited'), None, subcategories
            else:
                response_dct['error_message'] = _(u"There are missing field(s)"
                                        u" and/or errors in the submited form.")
        else:
            form = item_form(instance=init_item, subcategories=listed_subcats)
            formset_multi = multimediafile_formset(initial=init_multi,
                                                  prefix='multimedia')
            formset_picture = picturefile_formset(initial=init_picture,
                                                 prefix='picture')
        return None, (item_id, init_item, response_dct, form, formset_multi,
                      formset_picture), subcategories
    return func

get_edit_marker = get_edit_page('chimere:edit', Marker, MarkerForm)

def edit(request, area_name="", item_id=None, submited=False):
    """
    Edition page
    """
    response, values, sub_categories = get_edit_marker(request, area_name,
                                                       item_id, ['M', 'B'])
    if response:
        return response
    item_id, init_item, response_dct, form, formset_multi, formset_picture = \
                                                                        values
    # get the "manualy" declared_fields. Ie: properties
    declared_fields = form.declared_fields.keys()
    declared_fields = PropertyModel.objects.filter(available=True).all()
    filtered_properties = PropertyModel.objects.filter(available=True,
                                subcategories__id__isnull=False).all()
    point_value = init_item.point if init_item else None
    if request.POST and request.POST.get('point'):
        point_value = request.POST.get('point')
    response_dct.update({
        'actions':actions,
        'action_selected':('contribute', 'edit'),
        'map_layer':settings.CHIMERE_DEFAULT_MAP_LAYER,
        'form':form,
        'formset_multi':formset_multi,
        'formset_picture':formset_picture,
        'dated':settings.CHIMERE_DAYS_BEFORE_EVENT,
        'extra_head':form.media,
        'marker_id':item_id,
        'sub_categories':sub_categories,
        'point_widget':PointChooserWidget().render('point',
              point_value,
              area_name=response_dct['area_name']),
        'properties':declared_fields,
        'filtered_properties':filtered_properties,
        'submited':submited
    })
    # manualy populate the custom widget
    if 'subcategory' in form.data and form.data['subcategory']:
        response_dct['current_category'] = int(form.data['subcategory'])
    return render_to_response('chimere/edit.html', response_dct,
                              context_instance=RequestContext(request))

def uploadFile(request, category_id='', area_name=''):
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    Form = FileForm if not category_id else FullFileForm
    category = None
    if category_id:
        try:
            category = SubCategory.objects.get(pk=category_id)
            response_dct['category'] = unicode(category)
        except:
            pass
    # If the form has been submited
    if request.method == 'POST':
        form = Form(request.POST, request.FILES)
        # All validation rules pass
        if form.is_valid():
            raw_file = form.cleaned_data['raw_file']
            name = raw_file.name.split('.')[0]
            file_type = raw_file.name.split('.')[-1][0].upper()
            routefile = RouteFile(raw_file=raw_file, name=name,
                                  file_type=file_type)
            routefile.save()
            if not category_id:
                response_dct['gpx_id'] = routefile.pk
                return render_to_response('chimere/upload_file.html',
                         response_dct, context_instance=RequestContext(request))
            routefile.process()
            if not routefile.route:
                response_dct['errors'] = _(u"Bad file. Please check it with an "
                                           u"external software.")
                response_dct.update({'form':form})
                return render_to_response('chimere/upload_file.html',
                         response_dct, context_instance=RequestContext(request))
            route = Route(name=form.cleaned_data['name'], route=routefile.route,
                          associated_file=routefile, status='S')
            route.save()
            route.categories.add(category)
            route.save()
            response_dct['thanks'] = True
            form = Form()
    else:
        # An unbound form
        form = Form()
    response_dct.update({'form':form})
    return render_to_response('chimere/upload_file.html', response_dct,
                              context_instance=RequestContext(request))

def processRouteFile(request, area_name='', file_id=None):
    if file_id:
        try:
            route_file = RouteFile.objects.get(pk=file_id)
            route_file.process()
            route = route_file.route
            if not route:
                return HttpResponse(status=500)
            return HttpResponse('('+simplejson.dumps({'wkt':route,
                                                  'file_id':file_id})+')',
                                'application/javascript', status=200)
        except OSError as e:
            return HttpResponse(e.strerror, status=500)
    else:
        return HttpResponse(status=400)

get_edit_route = get_edit_page('chimere:editroute', Route, RouteForm)

def editRoute(request, area_name="", item_id=None, submited=False):
    """
    Route edition page
    """
    response, values, sub_categories = get_edit_route(request, area_name,
                                                       item_id, ['R', 'B'])
    if response:
        return response
    item_id, init_item, response_dct, form, formset_multi, formset_picture = \
                                                                        values

    # get the "manualy" declared_fields. Ie: properties
    declared_fields = form.declared_fields.keys()
    if 'description' in declared_fields:
        declared_fields.pop(declared_fields.index('description'))
    route_value = init_item.route if init_item else None
    if request.POST and request.POST.get('route'):
        route_value = request.POST.get('route')
    response_dct.update({
        'actions':actions,
        'action_selected':('contribute', 'edit-route'),
        'error_message':'',
        'map_layer':settings.CHIMERE_DEFAULT_MAP_LAYER,
        'form':form,
        'formset_multi':formset_multi,
        'formset_picture':formset_picture,
        'dated':settings.CHIMERE_DAYS_BEFORE_EVENT,
        'extra_head':form.media,
        'sub_categories':sub_categories,
        'route_widget':RouteChooserWidget().render('route', route_value,
                       area_name=response_dct['area_name'], routefile_id='',),
        'properties':declared_fields,
        'submited':submited
    })
    # manualy populate the custom widget
    if 'subcategory' in form.data and form.data['subcategory']:
        response_dct['current_category'] = int(form.data['subcategory'])
    return render_to_response('chimere/edit_route.html', response_dct,
                              context_instance=RequestContext(request))

def submited(request, area_name="", action=""):
    """
    Successful submission page
    """
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    response_dct.update({'actions':actions, 'action_selected':action,})
    return render_to_response('chimere/submited.html', response_dct,
                              context_instance=RequestContext(request))

def charte(request, area_name=""):
    """
    Affichage de la charte
    """
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    response_dct.update({'actions':actions, 'action_selected':('charte',)})
    return render_to_response('chimere/charte.html', response_dct,
                              context_instance=RequestContext(request))

def contactus(request, area_name=""):
    """
    Contact page
    """
    form = None
    msg = ''
    # If the form has been submited
    if request.method == 'POST':
        form = ContactForm(request.POST)
        # All validation rules pass
        if form.is_valid():
            response = notifyStaff(_(u"Comments/request on the map"),
                     form.cleaned_data['content'], form.cleaned_data['email'])
            if response:
                msg = _(u"Thank you for your contribution. It will be taken "\
                        u"into account. If you have left your email you may "\
                        u"be contacted soon for more details.")
            else:
                msg = _(u"Temporary error. Renew your message later.")
    else:
        form = ContactForm()
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    response_dct.update({'actions':actions, 'action_selected':('contact',),
                         'contact_form':form, 'message':msg})
    return render_to_response('chimere/contactus.html', response_dct,
                              context_instance=RequestContext(request))

def getDetail(request, area_name, marker_id):
    '''
    Get the detail for a marker
    '''
    try:
        marker = Marker.objects.filter(id=int(marker_id),
                                       status__in=['A', 'S'])[0]
    except (ValueError, IndexError):
        return HttpResponse('no results')
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    response_dct['marker'] = marker
    if request.method == 'GET':
        if 'simple' in request.GET and request.GET['simple']:
            response_dct['simple'] = True
    parameters = u'current_feature=%s' % marker_id
    parameters += u"&checked_categories=%s" % "_".join([str(m.id) \
                                              for m in marker.categories.all()])
    net_dct = getTinyfiedUrl(request, parameters, response_dct['area_name'])
    share_networks = []
    response_dct['share_url'] = net_dct['url']
    for network in settings.CHIMERE_SHARE_NETWORKS:
        share_networks.append((network[0], network[1] % net_dct, network[2]))
    response_dct['share_networks'] = share_networks
    # to be sure there is unique IDs during a browsing
    response_dct['time_now'] = datetime.datetime.now().strftime('%H%M%S')
    response_dct['dated'] = settings.CHIMERE_DAYS_BEFORE_EVENT \
                            and marker.start_date
    return render_to_response('chimere/detail.html', response_dct,
                              context_instance=RequestContext(request))

def getDescriptionDetail(request, area_name, category_id):
    '''
    Get the description for a category
    '''
    try:
        category = Category.objects.filter(id=int(category_id))[0]
    except (ValueError, IndexError):
        return HttpResponse('no results')
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    response_dct['category'] = category
    return render_to_response('chimere/category_detail.html', response_dct,
                              context_instance=RequestContext(request))

def checkDate(q):
    """
    Filter a queryset to manage dates
    """
    if not settings.CHIMERE_DAYS_BEFORE_EVENT:
        return q
    today = datetime.date.today()
    after = today + datetime.timedelta(settings.CHIMERE_DAYS_BEFORE_EVENT)

    q = q & (  Q(start_date__isnull=True)
             | Q(start_date__gte=today, start_date__lte=after)
             | Q(start_date__lte=today, end_date__gte=today)
            )
    return q

def getGeoObjects(request, area_name, category_ids, status):
    '''
    Get the JSON for markers and routes
    '''
    if not status:
        status = 'A'
    status = status.split('_')
    category_ids = category_ids.split('_')
    try:
        q = checkDate(Q(status__in=status, categories__in=category_ids))
        query = Route.objects.filter(q)
    except:
        return HttpResponse('no results')
    query.order_by('categories')
    routes = list(query)
    jsons = []
    current_cat, colors, idx = None, None, 0
    for route in routes:
        c_cat = route.categories.all()[0]
        if not current_cat or current_cat != c_cat:
            idx = 0
            current_cat = c_cat
            colors = list(Color.objects.filter(color_theme = c_cat.color_theme))
        if colors:
            jsons.append(route.getGeoJSON(color=colors[idx % len(colors)].code))
        else:
            jsons.append(route.getGeoJSON(color='000'))
        idx += 1
    try:
        q = checkDate(Q(status__in=status, categories__in=category_ids))
        query = Marker.objects.filter(q).distinct('pk').order_by('pk')
    except:
        return HttpResponse('no results')
    category_ids = [int(cat_id) for cat_id in category_ids]
    jsons += [geo_object.getGeoJSON(category_ids) for geo_object in list(query)]
    if not jsons:
        return HttpResponse('no results')
    data = '{"type": "FeatureCollection", "features":[%s]}' % ",".join(jsons)
    return HttpResponse(data)

def get_available_categories(request, area_name=None, area=None, status='A',
                             force=None):
    '''
    Get categories for a designed area
    '''
    context_data, redir = get_base_response(area_name)
    area = context_data["area"]
    if redir:
        return redir
    if area and area.dynamic_categories and \
       not "current_extent" in request.GET:
        context_data['sub_categories'] = []
        return render_to_response('chimere/blocks/categories.html', context_data,
                                       context_instance=RequestContext(request))
    if not area or not area.dynamic_categories:
        # Categories are not updated dynamicaly when the user move the map
        # so we return ALL the categories
        subcategories = SubCategory.getAvailable(
                                            area_name=context_data['area_name'])
        context_data['sub_categories'] = subcategories
        return render_to_response('chimere/blocks/categories.html', context_data,
                                       context_instance=RequestContext(request))
    default_message = "<p class='warning'>%s</p>" % \
                                        _("No category available in this area.")
    if not "status" in request.GET: # there must be a status
        status = 'A'
    try:
        status = status.split('_')
        current_extent = request.GET["current_extent"].replace('M', '-')\
                                                      .replace('D', '.')
        area = SimpleArea([float(pt) for pt in current_extent.split('_')])
    except:
        # bad extent format
        return HttpResponse(default_message)
    # if not force and area.isIn(SimpleArea(cookie.AREA):return
    categories = area.getCategories(status, area_name=context_data['area_name'])
    if not categories:
        return HttpResponse(default_message)
    get_cat = lambda subcat: subcat.category
    get_cat_order = lambda subcat: (subcat.category.order, subcat.category,
                                    subcat.order)
    categories = sorted(categories, key=get_cat_order)
    subcategories = [(cat, list(subcats)) \
                               for cat, subcats in groupby(categories, get_cat)]
    context_data['sub_categories'] = subcategories
    return render_to_response('chimere/blocks/categories.html', context_data,
                                       context_instance=RequestContext(request))

def getTinyfiedUrl(request, parameters, area_name=''):
    '''
    Get the tinyfied version of parameters
    '''
    data = {"urn": "", "url":"", "text":""}
    try:
        urn = TinyUrl.getUrnByParameters(parameters)
    except:
        return {}
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    url = reverse('chimere:tiny', args=[(response_dct['area_name'] \
                         if response_dct['area_name'] else '') + '/', urn])
    if not url.startswith('http'):
        url = get_base_uri(request) + url
    url = re.sub("([^:])\/\/", "\g<1>/", url)
    text = settings.PROJECT_NAME
    if 'current_feature' in parameters:
        for item in parameters.split('&'):
            if 'current_feature' in item:
                try:
                    text = unicode(Marker.objects.get(id=item.split('=')[1]))
                except (IndexError, Marker.DoesNotExist):
                    pass
    data["urn"] = urlquote(urn)
    data["url"] = urlquote(url)
    data["text"] = urlquote(text)
    return data

def redirectFromTinyURN(request, area_name='', tiny_urn=''):
    """
    Redirect from a tiny Urn
    """
    parameters = '?' + TinyUrl.getParametersByUrn(tiny_urn)
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    return HttpResponseRedirect(response_dct['extra_url'] + parameters)

def rss(request, area_name=''):
    '''
    Redirect to RSS subscription page
    '''
    response_dct, redir = get_base_response(area_name)
    if redir:
        return redir
    response_dct.update({'actions':actions, 'action_selected':('rss',),
                         'category_rss_feed':'',})
    # If the form has been submited
    if request.method == "POST":
        # User has defined the kind of POI he is interested in : POI in a area
        # (GET method is used for the link with RSS icon in the browser)
        if 'rss_category' in request.POST:
            #User wants to follow all the new POI
            if request.POST['rss_category'] == 'global':
                feeds_link = reverse('chimere:feeds-global')
                return redirect(feeds_link)
            # User wants to follow all the new POI by category or subcategory
            elif request.POST['rss_category'] == 'poi':
                response_dct['category_rss_feed'] = 'category'
                response_dct['sub_categories'] = SubCategory.getAvailable()
                return render_to_response('chimere/feeds/rss.html',
                                  response_dct,
                                  context_instance=RequestContext(request))
            # User wants to follow all the new POI situated in a defined area
            elif request.POST['rss_category'] == 'area':
                # An unbound form
                form = AreaForm()
                area_widget = AreaWidget().render('area', None)
                response_dct.update({
                    'map_layer':settings.CHIMERE_DEFAULT_MAP_LAYER,
                    'extra_head':form.media,
                    'form':form,
                    'category_rss_feed':'area',
                    'area_id':Area.getAvailable(),
                    'area_widget':area_widget
                })
                return render_to_response('chimere/feeds/rss.html',
                                  response_dct,
                                  context_instance=RequestContext(request))
            # Error when submitting the form
            else:
                error = _("Incorrect choice in the list")
                response_dct.update({'error_message':error,
                    'category_rss_feed':'',
                    'sub_categories':SubCategory.getAvailable()})
                return render_to_response('chimere/feeds/rss.html',
                                  response_dct,
                                  context_instance=RequestContext(request))

        # User has specified the category or subcategory he wants to follow =>
        # we redirect him towards the related rss feed
        if 'subcategory' in request.POST and request.POST['subcategory'] != '':
            cat_id = request.POST['subcategory']
            if cat_id.find("cat_") != -1 :
                cat_id = cat_id.split('_')[1]
                feeds_link = reverse('chimere:feeds-cat',
                                     kwargs={'category_id':cat_id})
                return redirect(feeds_link)

            else:
                feeds_link = reverse('chimere:feeds-subcat',
                                     kwargs={'category_id':cat_id})
                return redirect(feeds_link)

        # User has specified the ID of the area he wants to follow
        if 'id_area' in request.POST and request.POST['id_area'] != '':
            feeds_link = reverse('chimere:feeds-areaid',
                                 kwargs={'area_id':request.POST['id_area']})
            return redirect(feeds_link)

        # User has specified the area  he wants to follow => we redirect him
        # towards the related rss feed (using upper left and lower right
        # coordinates)
        elif 'upper_left_lat' in request.POST and \
             request.POST['upper_left_lat'] != '' and \
             'upper_left_lon' in request.POST and \
             request.POST['upper_left_lon'] != '' and \
             'lower_right_lon' in request.POST and \
             request.POST['lower_right_lon'] != '' and \
             'lower_right_lat' in request.POST and \
             request.POST['lower_right_lat'] != '' :
            coords = request.POST['upper_left_lat'] + '_' + \
                     request.POST['upper_left_lon'] + '_' + \
                     request.POST['lower_right_lat'] + '_' + \
                     request.POST['lower_right_lon']
            feeds_link = reverse('chimere:feeds-area',
                                 kwargs={'area':coords})
            return redirect(feeds_link)

    # GET method is used for linking with the RSS icon in the browser when user
    # wants to choose a category to follow
    elif request.method == "GET" and 'rss_category' in request.GET:
        if request.GET['rss_category'] == 'global':
            feeds_link = reverse('chimere:feeds-global')
            return redirect(feeds_link)
        if request.GET['rss_category'] == 'poi':
            response_dct['category_rss_feed'] = 'category'
            response_dct['sub_categories'] = SubCategory.getAvailable(['M','B'])
            return render_to_response('chimere/feeds/rss.html', response_dct,
                                      context_instance=RequestContext(request))
        if request.GET['rss_category'] == 'area':
            # An unbound form
            form = AreaForm()
            response_dct.update({'map_layer':settings.MAP_LAYER,
                            'extra_head':form.media,
                            'form':form,
                            'category_rss_feed':'area',
                            'area_id':Area.getAvailable(),
                            'area_widget':AreaWidget().render('area', None)})
            return render_to_response('chimere/feeds/rss.html', response_dct,
                                      context_instance=RequestContext(request))

    # User access to the RSS tab
    else:
        return render_to_response('chimere/feeds/rss.html', response_dct,
                                  context_instance=RequestContext(request))
