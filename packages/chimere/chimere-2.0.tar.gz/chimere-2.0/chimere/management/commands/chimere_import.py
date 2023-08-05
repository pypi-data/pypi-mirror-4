#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import datetime, time

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from chimere.models import Importer
from chimere import tasks

class Command(BaseCommand):
    args = '<import_id>'
    help = "Launch import from an external source. Import configuration must "\
           "be beforehand inserted in the database with the web admin."

    def handle(self, *args, **options):
        imports = dict([(imp.pk, imp)
                       for imp in Importer.objects.order_by('pk').all()])
        imprt = None
        if args and args[0]:
            try:
                imprt = Importer.objects.get(pk=int(args[0]))
            except (ValueError, ObjectDoesNotExist):
                raise CommandError("Import with ID '%s' doesn't exist." % \
                                                                        args[0])
        if not args:
            while not imprt:
                self.stdout.write('* Choose the import: \n')
                for k in imports:
                    self.stdout.write(' %s\n' % unicode(imports[k]).encode(
                                                             'ascii', 'ignore'))
                self.stdout.flush()
                self.stdout.write('\nImport ID: ')
                v = raw_input()
                try:
                    imprt = Importer.objects.get(pk=int(v))
                except (ValueError, ObjectDoesNotExist):
                    self.stdout.write("Import with ID '%s' doesn't exist.\n\n" \
                                      % v)
        pending_state = unicode(tasks.IMPORT_MESSAGES['import_pending'][0])
        imprt.state = pending_state
        imprt.save()
        tasks.importing(imprt.pk)
        self.stdout.write("Import '%d' in progress...\n" % imprt.pk)
        self.stdout.flush()
        state = pending_state
        while state == pending_state:
            time.sleep(1)
            state = Importer.objects.get(pk=int(imprt.pk)).state
        self.stdout.write(state + '\n')

