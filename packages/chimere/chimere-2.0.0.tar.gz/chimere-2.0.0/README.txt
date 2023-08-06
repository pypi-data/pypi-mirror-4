=======
Chimère
=======

Chimère is a cartographic mashup using OpenStreetMap as a default map layer.
This software aims to create online collaborative and thematic maps. Content
(multimedia, text) are associated to basic geographics items (Point Of Interest,
routes). Add on the map are open to everybody with no authentification but are
moderated by a team in charge of the map.

Features:
 - Display (by default) of the mapnik OpenStreetMap layer.
 - Display on the map of POIs (with markers) and routes (with colored
   polylines).
 - Thematic choices of items to display (POIs and routes).
 - Filter themes in regard to currently available items.
 - Display of the detail of a POI (name, description, pictures, multimedia
   files).
 - Add of a cartographic item (POI, route) on the map by an user without
   authentication (the item is only available after moderation).
 - Admin interface for moderation and configuration.
 - Cut a Chimère by "areas". Each "area" can have specific themes, a new default
   center, welcome message, bounding box, allow of restriction to a bounding
   box, activation of dynamic themes, available themes, themes checked by
   default.
 - Import and export of data. Available formats are: ShapeFile, KML, GeoRSS
   (import only), CSV and OSM.
 - Configuration of map layers in administration interface. By default these
   cartographic items are available: OSM Mapnik, MapQuest, OSM Transport,
   Cyclemap.


Full documentation is available on `Read the docs <http://chimere.readthedocs.org/en/latest/>`_.

External libs
=============

To be fully functional, this package is provided with external libs:
 - `OsmApi <http://wiki.openstreetmap.org/wiki/PythonOsmApi>`_ - GPL v3.
 - `prettyPhoto <http://www.no-margin-for-errors.com/projects/prettyphoto-jquery-lightbox-clone/>`_ - GPL v2.
 - `jMediaelement <https://github.com/aFarkas/jMediaelement>`_ - GPL v2.
