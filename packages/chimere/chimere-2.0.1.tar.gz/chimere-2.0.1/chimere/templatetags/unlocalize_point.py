#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
import re

register = template.Library()

def unlocalize_point(value):
    """
    Basic unlocalize filter for django 1.2
    """
    return unicode(value).replace(',', '.')

register.filter(unlocalize_point)

