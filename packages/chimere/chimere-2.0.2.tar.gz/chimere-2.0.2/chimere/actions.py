#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008-2010  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
Actions available in the main interface
"""
from django.conf import settings
from django.contrib.auth import models
from django.utils.translation import ugettext_lazy as _

class Action:
    def __init__(self, id, path, label):
        self.id, self.path, self.label = id, path, label

actions = [(Action('view', '', _('View')), []),
           (Action('contribute', 'edit/', _('Contribute')),
                    (Action('edit', 'edit/', _('Add a new point of interest')),
                     Action('edit-route', 'edit-route/', _('Add a new route'))),
           ),]

if settings.CHIMERE_FEEDS:
    actions.append((Action('rss', 'feeds', _('RSS feeds')), []))

if settings.EMAIL_HOST:
    actions.append((Action('contact', 'contact', _('Contact us')), []),)

