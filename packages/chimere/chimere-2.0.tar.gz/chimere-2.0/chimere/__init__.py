#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'example_project.settings'

from django.utils.translation import ugettext as _

try:
    # strings to be considered for translation
    # templates/chimere/edit.html, templates/chimere/edit_route.html
    _(u"Multimedia files")
    _(u"Picture files")
except ImportError:
    pass

VERSION = (2, 0)

def get_version():
    return u'.'.join((unicode(num) for num in VERSION))

__version__ = get_version()
