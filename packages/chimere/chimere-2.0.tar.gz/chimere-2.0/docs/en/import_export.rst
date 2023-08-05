.. -*- coding: utf-8 -*-

=============
Import/export
=============

:Author: Étienne Loks
:date: 2012-11-28
:Copyright: CC-BY 3.0

This document presents the import/export functionnalities of Chimère.
It has been updated for version 2.0.0.

.. _importing:

Importing
---------

In Chimère the import mechanism is based on **Import object**. These objects
are stored in database to keep trace of imports and to facilitate the
re-importation from the same source. In fact if possible the update of data from
a same type of source is managed. 

.. Note::
    The ability to do such updates depends on the existence of a unique id 
    for each object on your source.

To add an **Import object** you need to go to *Chimere > Imports* then **Add**.

After that you'll have to select your source type and then the form depends on
this source type.

Common fields
*************

- **Name by default**: if no name can be identified to the newly imported object
  this is the name that will be used. If this field is empty the name of the
  associated category will be use.
- **SRID**: Chimère will try to identify automatically the correct coordinate
  system from the given source. But sometimes the information is not present or
  cannot be guessed (for instance a Shapefile that uses non standard proj file).
  In this case Chimère will use WGS84 by default (the classic
  latitude/longitude) but it is not always correct. If you experience problems
  with items localisation you should put here the `SRID
  <https://en.wikipedia.org/wiki/SRID>`_ associated to the coordinate system of
  your source.
- **Overload existing data**: by default when data is updated on the source and
  has been changed in your Chimère instance a new item is created and has to
  be reconciled with the :ref:`amendment form <managing-modified>`. If you don't
  want to use this form and then overwrite with the data from the external
  source, check this option.
- **Origin**: if not null this field will be associated to each item imported in
  order to easily identify where the item came from. For OSM import the source
  is automatically added.
- **License**: if not null this field will be associated to each item imported in
  order to easily identify the license associated to the item. For OSM import
  the license is automatically added.
- **Associated subcategories (mandatory)**: The selected subcategories will be
  associated to newly imported items.


KML import
**********

.. image:: static/chimere_admin_import_KML.png


- **Web address/source file (mandatory)**: your KML could be distant or a local
  file. You'll have to fill one of the two fields.
- **Filter**: if you want to import only a specific *Folder* of your KML file
  put his name on this field.
- **Zipped file**: if your source is a KMLZ file (a zipped KML), check this case.

Shapefile import
****************

.. image:: static/chimere_admin_import_shapefile.png


- **Web address/source file (mandatory)**: your Shapefile could be distant or a 
  local file. You'll have to fill one of the two fields.
- **Zipped file**: only zipped Shapefiles are accepted so this checkbox has to be
  checked.

GeoRSS import
*************

Simple GeoRSS and W3C GeoRSS are managed.

.. image:: static/chimere_admin_import_georss.png

- **Web address (mandatory)**: only distant GeoRSS are managed.

CSV import
**********

The format of the CSV file (number and order of columns) managed by Chimère 
varies depending on the properties you have added on your Chimère instance.
So we recommend you to first do an export of some items in CSV with Chimère. 
The CSV format of the exported file will meet Chimère requirements.

By the way because of the geometry of the item this format is not very 
convenient to add new content but could be handy to update informations.

.. Warning::
   If you mean to update existing data by this import, unless you know how to
   edit WKT do *not* modify the geometry column.

.. image:: static/chimere_admin_import_CSV.png

- **Web address/source file (mandatory)**: your CSV file could be distant or a
  local file. You'll have to fill one of the two fields.

.. _osm-import:

OpenStreetMap import
********************

.. image:: static/chimere_admin_import_OSM.png

To import from OSM Chimère use the XAPI API of OSM.

- **Web address (mandatory)**: XAPI url used to import data. This field should
  be filled with a default address. By default the MapQuest server is used as it
  seems to be the more robust. If you experience problems with OSM import, check
  the availability of the XAPI server used and eventually change it.
- **Filter area (mandatory)**: draw the bounding box you want to use for your
  OSM import.
- **Filter type (mandatory)**: choose if you want to import way or nodes.
- **Filter tag (mandatory)**: choose the OSM key/value couple used to filter OSM
  data. A link to the `OSM Map features page
  <https://wiki.openstreetmap.org/wiki/Map_Features>`_ is provided to help you
  find appropriate values.
- **Refresh button**: this button convert your choices to appropriate XAPI args.
  You have to hit this button before validating the form.

Importing
*********

Once your new import item created, select it in the import object list, choose
the **Import** action and validate.

The import should be processing normally. If not, an explicit error message
should be printed in the state column of your import.

You can also launch imports with the CLI (ideal for crontab jobs). In the
project directory you only need to launch the command::

    ./manage.py chimere_import <import_id>

- *import_id* is the import ID

If you launch the command without *import_id* the list of imports available is
presented and you can choose one.

.. _manage-imported-data:

Managing imported data
**********************

All new imported items have the state **Imported**. To make them available on
the map you'll have to validate them. If you don't want some items to be visible
on the map, instead of deleting them it is recommended to set them to the state
**Disabled**. So on the next update from the source, rather than appear as new
items they remain disabled.

.. Warning::
   Be careful with duplicates between your existing data and imported data. This
   is particularly important if you want to export your data to OSM.

Exporting
---------

Export to CSV/KML/Shapefile
***************************

Directly from the :ref:`geographic items list <geographic-items-management>` you
can export to the chosen format. All you have to do is to select the desired
items, choose the appropriate action in the action list and validate.

You can also launch exports with the CLI (ideal for crontab jobs). In the
project directory you only need to launch the command::

    ./manage.py chimere_export <subcategory_id> <CSV|KML|SHP> \
                               <marker|route> <filename>

- *subcategory_id* is the ID of the chosen subcategory
- *CSV|KML|SHP* is the chosen format
- *marker|route* is to get marker or route
- *filename* is the output filename

If you launch the command without arguments you will be prompted for the choice
to make for your export.


Export to OSM
*************

.. Warning::
   If you are not sure of what you are doing with OSM export: don't do it! It is
   really important to not mess with others' data.

.. Note::
    Only export of OSM nodes are managed.

OSM export is not that easily managed. First (if not yet done) you'll have to
define an import (:ref:`see above <osm-import>` for details). This will enable
to determine:

- the area concerned by your export.
- the key/value tag to append to your new/updated items.
- the subcategories concerned by your export. If you think that some items in
  these subcategories should not be in OSM database (because there are not
  relevant or because of license issues) beforehand mark them as **Not for OSM**
  in the *import fields* of the :ref:`geographic items forms
  <geographic-items-management>`.


The OSM export in Chimère is designed to be the more preservative possible in
regards to OSM database. That's why before any export an import is done. If
the new import has updated data, treat them before doing an export (cf.
:ref:`manage imported data <manage-imported-data>`).

To launch an export select the appropriate *Import* object in the imports list.
Then select the **Export to OSM** action and validate.
Then you'll be asked for your OSM username and password and the API you want to
use. If you regularly use Chimère to do export, it is recommended to create an
OSM specific account for that.
The test API is available to make export test. If you want to use the test
API you'll have to create a specific account on the test platform.

.. Warning::
   The data on the test platform are not synced with the main platform. You won't
   have the same data than the ones you got with XAPI.

Once all this field filled, you can (finally!) launch the export.

When exporting tags are automatically added/updated:

- *name*: get from the item name in Chimère.
- *source*: to identify Chimère as a source.
