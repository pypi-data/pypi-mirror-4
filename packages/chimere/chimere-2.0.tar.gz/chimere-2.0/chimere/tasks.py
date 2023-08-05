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

from django.conf import settings
if 'kombu.transport.django' in settings.INSTALLED_APPS \
   and 'djcelery' in settings.INSTALLED_APPS:
    from celery.decorators import task

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from chimere.models import Importer
from external_utils import OsmApi


def single_instance_task(timeout):
    def task_exc(func):
        def wrapper(*args, **kwargs):
            return func()
        return wrapper
    return task_exc

if 'task' in globals():
    def single_instance_task(timeout):
        def task_exc(func):
            def wrapper(*args, **kwargs):
                lock_id = "celery-single-instance-" + func.__name__
                acquire_lock = lambda: cache.add(lock_id, "true", timeout)
                release_lock = lambda: cache.delete(lock_id)
                if acquire_lock():
                    try:
                        func(*args, **kwargs)
                    finally:
                        release_lock()
            return wrapper
        return task_exc
else:
    def task():
        def task_exc(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
            return wrapper
        return task_exc

IMPORT_MESSAGES = {
                   'import_pending':[_(u"Import pending")],
                   'import_process':[_(u"Import processing")],
                   'import_done':[_(u"Import successfuly done"),
                    _(u" %(new)d new item(s), %(updated)d updated item(s)")],
                   'import_failed':[_(u"Import failed"), "%s"],
                   'import_cancel':[_(u"Import canceled")],
                   'export_pending':[_(u"Export pending")],
                   'export_process':[_(u"Export processing")],
                   'export_done':[_(u"Export successfuly done"),
                    _(u" %(updated)d updated item(s)")],
                   'export_failed':[_(u"Export failed"), "%s"],
                   'export_cancel':[_(u"Export canceled")]
                   }

@task()
def importing(importer_pk):
    try:
        importer = Importer.objects.get(pk=importer_pk)
    except ObjectDoesNotExist:
        # importer doesn't exists anymore: too late!
        return
    if importer.state != IMPORT_MESSAGES['import_pending'][0]:
        # import canceled or done
        return
    importer.state = unicode(IMPORT_MESSAGES['import_process'][0])
    importer.save()
    new_item, updated_item, error = importer.manager.get()
    importer.state = error + ' ' if error else ''
    importer.state += unicode(IMPORT_MESSAGES['import_done'][0])
    importer.state += u" - " \
         + unicode(IMPORT_MESSAGES['import_done'][1]) % {'new':new_item,
                                                         'updated':updated_item}
    importer.state = importer.state[:200]
    importer.save()
    return True

@task()
@single_instance_task(60*10)
def exporting(importer_pk, extra_args=[]):
    try:
        importer = Importer.objects.get(pk=importer_pk)
    except ObjectDoesNotExist:
        # importer doesn't exists anymore: too late!
        return
    if importer.state != IMPORT_MESSAGES['export_pending'][0]:
        # import canceled or done
        return
    importer.state = unicode(IMPORT_MESSAGES['export_process'][0])
    importer.save()
    error = None
    try:
        updated_item, error = importer.manager.put(extra_args)
    except OsmApi.ApiError, error:
        pass
    if error:
        importer.state = unicode(IMPORT_MESSAGES['export_failed'][0]) \
              + u" - " + unicode(IMPORT_MESSAGES['export_failed'][1]) % error
        importer.save()
        return
    importer.state = unicode(IMPORT_MESSAGES['export_done'][0]) + u" - " \
         + unicode(IMPORT_MESSAGES['export_done'][1]) % {'updated':updated_item}
    importer.save()
    return True
