#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.db import connection, transaction

cursor = connection.cursor()

from main.models import Area, Marker, Route, Icon, SubCategory
from django.contrib.gis.geos import LineString

# early versions before 0.1: urn field doesn't exist for area

import htmlentitydefs, re

def slugfy(text, separator):
    ret = u""
    text = text.strip()
    for c in text.lower():
        try:
           ret += htmlentitydefs.codepoint2name[ord(c)][0]
        except:
            ret += c
    ret = re.sub("\W", " ", ret)
    ret = re.sub(" +", separator, ret)
    return ret.strip()

QUERY_CHECK_FIELD = """SELECT a.attname AS field FROM pg_class c, pg_attribute a
    WHERE c.relname = '%s' AND a.attnum > 0 AND a.attrelid = c.oid
          AND a.attname='%s';"""
QUERY_CHECK_TABLE = """SELECT c.relname FROM pg_class c
WHERE c.relname = '%s';"""


query = QUERY_CHECK_FIELD % ('main_area', 'urn')
cursor.execute(query)
transaction.commit_unless_managed()

row = cursor.fetchone()
if not row:
    query_update = "ALTER TABLE main_area ADD COLUMN urn VARCHAR(50) \
UNIQUE"
    cursor.execute(query_update)
    transaction.commit_unless_managed()
    areas = Area.objects.all()
    print " * urn field created in table main_area"
    for area in areas:
        urn = slugfy(area.name, "-")
        area.urn = urn
        area.save()
        print " * area %s urn is now: %s" % (area.name, area.urn)

    query = "ALTER TABLE main_area ALTER COLUMN urn SET not null;"
    cursor.execute(query)
    transaction.commit_unless_managed()
    print " * urn field has now the constraint NOT NULL"

from django.contrib.auth.models import Permission, ContentType

# check if permission have been correctly set for each areas
areas = Area.objects.all()
for area in areas:
    content_type = ContentType.objects.get(app_label="main",
            model="area")
    mnemo = 'change_area_' + area.urn
    perm = Permission.objects.filter(codename=mnemo)
    if not perm:
        lbl = "Can change " + area.name
        perm = Permission(name=lbl, content_type_id=content_type.id,
                          codename=mnemo)
        perm.save()
        print ' * permission "' + lbl + '" has been created'
        print " WARNING: don't forget to update administrator's rights with \
this new permission"

# early versions before 0.1: subcategory_areas table doesn't exist
# version 1.0 subcategory_areas renamed to main_subcategory_areas

query = QUERY_CHECK_TABLE % 'main_subcategory_areas'
cursor.execute(query)
transaction.commit_unless_managed()

row = cursor.fetchone()
if not row:
    query = QUERY_CHECK_TABLE % 'subcategory_areas'
    cursor.execute(query)
    transaction.commit_unless_managed()

    row = cursor.fetchone()
    if row:
        query_rename = "ALTER TABLE subcategory_areas RENAME TO \
main_subcategory_areas;"
        cursor.execute(query_rename)
        transaction.commit_unless_managed()
        print " * subcategory_areas renamed to main_subcategory_areas"
    else:
        query_create = """
CREATE TABLE "main_subcategory_areas" (
    "id" serial NOT NULL PRIMARY KEY,
    "subcategory_id" integer NOT NULL REFERENCES "main_subcategory" ("id")
                                                  DEFERRABLE INITIALLY DEFERRED,
    "area_id" integer NOT NULL REFERENCES "main_area" ("id")
                                                  DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("subcategory_id", "area_id"));
"""
        cursor.execute(query_create)
        transaction.commit_unless_managed()
        print " * main_subcategory_areas created"

# early versions before 0.1: main_tinyurl table doesn't exist

query = QUERY_CHECK_TABLE % 'main_tinyurl'
cursor.execute(query)
transaction.commit_unless_managed()

row = cursor.fetchone()
if not row:
    query_create = """
CREATE TABLE "main_tinyurl" (
    "id" serial NOT NULL PRIMARY KEY,
    "parameters" varchar(500) NOT NULL);
"""
    cursor.execute(query_create)
    transaction.commit_unless_managed()
    print " * main_tinyurl created"


# early versions before 0.1: save area with wrong SRID
# only errors with default SRID is managed adapt the script for your SRID

from osgeo import osr

srs = osr.SpatialReference()
srs.ImportFromEPSG(4326) # WGS84
ll = srs.CloneGeogCS()
srs.ImportFromEPSG(settings.EPSG_PROJECTION)
proj = osr.CoordinateTransformation(srs, ll)

changed = False
areas = Area.objects.all()
for area in areas:
    # only one test: assume each point as been save with the same SRID...
    if area.upper_left_corner.srid == 4326 and area.upper_left_corner.x > 90 \
                                           or area.upper_left_corner.x < -90:
        changed = True
        pt = proj.TransformPoint(area.upper_left_corner.y,
                                 area.upper_left_corner.x)
        area.upper_left_corner.x = pt[0]
        area.upper_left_corner.y = pt[1]
        pt = proj.TransformPoint(area.lower_right_corner.y,
                                 area.lower_right_corner.x)
        area.lower_right_corner.x = pt[0]
        area.lower_right_corner.y = pt[1]
        area.save()
if changed:
    print " * projections of areas corrected"

# changement from version 1.0 to 1.1: add dated fields to markers and routes
if settings.DAYS_BEFORE_EVENT:
    for cls in (Marker, Route):
        table = cls._meta.db_table
        query = QUERY_CHECK_FIELD % (table, 'start_date')
        cursor.execute(query)
        transaction.commit_unless_managed()

        row = cursor.fetchone()
        if not row:
            query_update = "ALTER TABLE "+table+" ADD COLUMN start_date date"
            cursor.execute(query_update)
            transaction.commit_unless_managed()
            query_update = "ALTER TABLE "+table+" ADD COLUMN end_date date"
            cursor.execute(query_update)
            transaction.commit_unless_managed()
            print " * start_date and end_date added to table " + table + "."

# changement from version 1.0 to 1.1: add available_date field to marker
if 'chimere.rss' in settings.INSTALLED_APPS:
    for cls in (Marker,):
        table = cls._meta.db_table
        query = QUERY_CHECK_FIELD % (table, 'available_date')
        cursor.execute(query)
        transaction.commit_unless_managed()

        row = cursor.fetchone()
        if not row:
            query_update = "ALTER TABLE " + table + " ADD COLUMN \
available_date timestamp with time zone"
            cursor.execute(query_update)
            transaction.commit_unless_managed()
            print " * available_date added to table " + table + "."

# changement from version 1.0 to 1.1: version of django 1.2
# create specific height and width for image fields

for cls, attr in ((Icon, "image"), (Marker, "picture"),
                  (Route, "picture")):
    table = cls._meta.db_table
    query = QUERY_CHECK_FIELD % (table, 'width')
    cursor.execute(query)
    transaction.commit_unless_managed()

    row = cursor.fetchone()
    if not row:
        query_update = "ALTER TABLE "+table+" ADD COLUMN width integer"
        cursor.execute(query_update)
        transaction.commit_unless_managed()
        query_update = "ALTER TABLE "+table+" ADD COLUMN height integer"
        cursor.execute(query_update)
        transaction.commit_unless_managed()
        for obj in cls.objects.all():
            image = getattr(obj, attr)
            if not image:
                continue
            obj.width = image.width
            obj.height = image.height
            obj.save()
        print " * height and width of " + table + " corrected"

# changement from version 1.0 to 1.1: multiple selection of categories

for cls in (Marker, Route):
    table = cls._meta.db_table[len("main_"):]
    query = QUERY_CHECK_TABLE % ('main_' + table + '_categories')
    cursor.execute(query)
    transaction.commit_unless_managed()

    row = cursor.fetchone()
    if row:
        continue
    query_create = """
CREATE TABLE "main_%s_categories" (
  "id" serial NOT NULL PRIMARY KEY,
  "%s_id" integer NOT NULL REFERENCES "main_%s" ("id") DEFERRABLE INITIALLY DEFERRED,
  "subcategory_id" integer NOT NULL REFERENCES "main_subcategory" ("id") DEFERRABLE INITIALLY DEFERRED,
  UNIQUE ("%s_id", "subcategory_id"));
""" % (table, table, table, table)
    cursor.execute(query_create)
    transaction.commit_unless_managed()
    for obj in cls.objects.all():
        query = "select subcategory_id from main_%s where id=%d" % (table,
                                                                    obj.id)
        cursor.execute(query)
        transaction.commit_unless_managed()

        row = cursor.fetchone()
        if row:
            obj.categories.add(SubCategory.objects.get(id=row[0]))
            obj.save()
    query = "ALTER TABLE main_%s DROP COLUMN subcategory_id;" % table
    cursor.execute(query)
    transaction.commit_unless_managed()
    print " * main_%s_categories created" % table

# -> version 1.2: associate point to route (for the future)
query = QUERY_CHECK_FIELD % ('main_marker', 'route_id')
cursor.execute(query)
transaction.commit_unless_managed()

row = cursor.fetchone()
if not row:
    query_update = 'ALTER TABLE "main_marker" ADD COLUMN \
"route_id" integer REFERENCES "main_route" ("id") DEFERRABLE INITIALLY DEFERRED'
    cursor.execute(query_update)
    transaction.commit_unless_managed()
    print " * route_id added to table main_marker."

# -> version 1.3: file associated to routes
query = QUERY_CHECK_TABLE % 'main_routefile'
cursor.execute(query)
transaction.commit_unless_managed()

row = cursor.fetchone()
if not row:
    query_create = """
    CREATE TABLE "main_routefile" (
            "id" serial NOT NULL PRIMARY KEY,
            "name" varchar(150) NOT NULL,
            "raw_file" varchar(100) NOT NULL,
            "simplified_file" varchar(100),
            "file_type" varchar(1) NOT NULL
            )
    ;
    ALTER TABLE "main_route" ADD COLUMN
                 "associated_file_id" integer REFERENCES "main_routefile" ("id")
                                                  DEFERRABLE INITIALLY DEFERRED;
    """
    cursor.execute(query_create)
    transaction.commit_unless_managed()
    print " * main_routefile created"

# early versions before 0.1: save route with wrong SRID
# only errors with default SRID is managed adapt the script for your SRID

changed = False
routes = Route.objects.all()
for route in routes:
    # only one test: assume each point as been save with the same SRID...
    if route.route and route.route.srid == 4326 and \
       route.route[0][0] > 90 or route.route[0][0] < -90:
        changed = True
        new_route = []
        for pt in route.route:
            pt = proj.TransformPoint(pt[0], pt[1])
            new_route.append((pt[0], pt[1]))
        route.route = LineString(new_route)
        route.save()
if changed:
    print " * projections of routes corrected"
