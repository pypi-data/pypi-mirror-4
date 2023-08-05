#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import datetime, time

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from chimere import tasks
from chimere.admin import export_to_csv, export_to_kml, export_to_shapefile
from chimere.models import Category, SubCategory, Marker, Route

EXPORTER = {'CSV':export_to_csv,
            'KML':export_to_kml,
            'SHP':export_to_shapefile}

class Command(BaseCommand):
    args = '<subcategory_id> <CSV|KML|SHP> <marker|route> <filename>'
    help = "Export items from a subcategory in CSV, KML or ShapeFile"

    def handle(self, *args, **options):
        subcat = None
        if args and args[0]:
            try:
                subcat = SubCategory.objects.get(pk=int(args[0]))
            except (ValueError, ObjectDoesNotExist) as e:
                raise CommandError("Sub-category with ID '%s' doesn't exist." %\
                                                                        args[0])
        while not subcat:
            self.stdout.write('Choose a sub-category:\n')
            for cat in Category.objects.order_by('order'):
                self.stdout.write('* %s\n' % cat.name)
                for subcat in cat.subcategories.order_by('order').all():
                    self.stdout.write(' %d - %s\n' % (subcat.pk, subcat.name))
            self.stdout.write('\nSub-category ID: ')
            self.stdout.flush()
            v = raw_input()
            try:
                subcat = SubCategory.objects.get(pk=v)
            except (ValueError, ObjectDoesNotExist) as e:
                subcat = None
                self.stdout.write("Sub-category with ID '%s' doesn't exist.\n\n"
                                  % v)
        frmat = None
        if args and args[1]:
            try:
                assert(args[1] in ('CSV', 'KML', 'SHP'))
            except AssertionError:
                raise CommandError("'%s' format is not managed." % args[1])
            frmat = args[1]
        while frmat not in ('CSV', 'KML', 'SHP'):
            self.stdout.write('Choose a format (CSV, KML or SHP): ')
            frmat = raw_input().replace('\n', '')
        exporter = EXPORTER[frmat]
        cls = None
        if args and args[2]:
            try:
                assert(args[2] in ('marker', 'route'))
            except AssertionError:
                raise CommandError("Exported item must be 'marker' or 'route'."
                                   % args[1])
            if args[2] == 'marker':
                cls = Marker
            elif args[2] == 'route':
                cls = Route
        while not cls:
            self.stdout.write('Choose an item type:\n 1 - marker\n 2 - route\n')
            self.stdout.write('Number: ')
            v = raw_input()
            if v == '1':
                cls = Marker
            elif v == '2':
                cls = Route
        filename = ''
        if args and args[3]:
            filename = args[3]
        else:
            self.stdout.write('Filename: ')
            filename = raw_input()
        response = exporter(None, None, cls.objects.filter(categories=subcat))
        try:
            with open(filename, 'w+') as fl:
                fl.write(response.content)
        except IOError as e:
            raise CommandError(e)
