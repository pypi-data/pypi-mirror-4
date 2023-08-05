#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script is used to migrate properties data in description field
# It is only used when migration to version 2.0

import sys
sys.path.append('.')
sys.path.append('..')

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.db import connection, transaction

cursor = connection.cursor()

from chimere.models import PropertyModel, Property

sys.stdout.write("""
This script is used to migrate properties data in the new description
field.
It is only useful when migrating to version 2.0.

WARNING: once the data is migrated the property model and all the
associated data are removed.

WARNING: this should be used only on a new migrated system: all previous
data in the new description field will be overload by the data from the
property model.

""")
response = None
while response not in ('y', 'n'):
    sys.stdout.write("Do you want to continue (y/n)? ")
    response = raw_input()
if response == "n":
    sys.exit(0)
if not PropertyModel.objects.count():
    sys.stdout.write("There is no property model available.\n")
    sys.exit(0)

sys.stdout.write("\nAvailable property models:\n")
property_models = list(PropertyModel.objects.all())
for idx, property_model in enumerate(property_models):
    sys.stdout.write(" * %d - %s\n" % (idx+1, property_model.name))

response = 0
while not (response > 0 and response <= len(property_models)):
    sys.stdout.write("Choose the property model to migrate: ")
    response = raw_input()
    try:
        response = int(response)
    except ValueError:
        response = 0

property_model = property_models[response-1]

while response not in ('y', 'n'):
    sys.stdout.write("Are you sure you want to migrate %s (y/n)? " % \
                     property_model.name)
    response = raw_input()
if response == "n":
    sys.exit(0)

idx = 0
for idx, property in enumerate(Property.objects.filter(
                                        propertymodel=property_model)):
    property.marker.description = property.value
    property.marker.save()

sys.stdout.write("* %d marker(s) updated.\n" % (idx+1))
Property.objects.filter(propertymodel=property_model).delete()
sys.stdout.write("* %d propertie(s) deleted.\n" % (idx+1))
property_model.delete()
sys.stdout.write("* Property model deleted.\n")

