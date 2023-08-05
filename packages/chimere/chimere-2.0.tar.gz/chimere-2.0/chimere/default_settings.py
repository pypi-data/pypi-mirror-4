# -*- coding: utf-8 -*-
"""
Here are the default settings for the Chimere app.
Feel free to set these settings in your project, they will override these defaults.
"""
# The height and width of the POI icons
CHIMERE_ICON_HEIGHT = 20
CHIMERE_ICON_WIDTH = 20
# The offset of the POI icons
CHIMERE_ICON_OFFSET_X = 0
CHIMERE_ICON_OFFSET_Y = 0

# default center of the map
CHIMERE_DEFAULT_CENTER = (2.49, 48.7)
# Default zoom level
CHIMERE_DEFAULT_ZOOM = 10
# projection used by the main map
# most public map providers use spherical mercator : 900913
CHIMERE_EPSG_PROJECTION = 900913
# projection displayed to the end user by openlayers
# chimere use the same projection to save its data in the database
CHIMERE_EPSG_DISPLAY_PROJECTION = 4326
# display of shortcuts for areas
CHIMERE_DISPLAY_AREAS = True
# number of day before an event to display
# if equal to 0: disable event management
# if you change this value from 0 to a value in a production environnement
# don't forget to run the upgrade.py script to create appropriate fields in
# the database
CHIMERE_DAYS_BEFORE_EVENT = 30

# JS definition of the main map cf. OpenLayers documentation for more details
CHIMERE_DEFAULT_MAP_LAYER = "new OpenLayers.Layer.OSM.Mapnik('Mapnik')" # OSM mapnik map

# display picture inside the description by default or inside a galery?
CHIMERE_MINIATURE_BY_DEFAULT = True
