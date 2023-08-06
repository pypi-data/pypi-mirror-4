#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

VERSION = (2, 0, 1)

def get_version():
    return u'.'.join((unicode(num) for num in VERSION))

__version__ = get_version()
