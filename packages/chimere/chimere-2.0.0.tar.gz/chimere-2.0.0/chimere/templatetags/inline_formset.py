#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext as _
import re

register = template.Library()

@register.inclusion_tag('chimere/blocks/inline_formset.html')
def inline_formset(caption, formset):
    u"""
    Render a formset as an inline table.
    For i18n of the caption Be carreful to add manualy the caption label to the
    translated fields
    """
    return {'caption':caption, 'formset':formset}

