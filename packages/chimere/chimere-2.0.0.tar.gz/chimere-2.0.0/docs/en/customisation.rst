.. -*- coding: utf-8 -*-

=============
Customisation
=============

:Author: Étienne Loks
:date: 2012-11-28
:Copyright: CC-BY 3.0

This document presents the customisation of Chimère.
It has been updated for version 2.0.0.


.. _managing-layers:

Managing layers
---------------

There are some different layers available by default in Chimère (OSM Mapnik, OSM
Mapquest, OSM Transport map, OSM Cyclemap). You can add some extra layer using
the web administration pages of Chimère. The new layer is defined with the
appropriate `Openlayers <http://openlayers.org/>`_ JS code. This JS code must
be a compatible Openlayers Layer instance with no ending semi-colon. For
instance defining a Bing layer can be done with this kind of code::

    new OpenLayers.Layer.Bing({
                name: "Aerial",
                key: "my-bing-API-key",
                type: "Aerial"})


Refer to the `Openlayers documentation API
<http://dev.openlayers.org/releases/OpenLayers-2.12/doc/apidocs/files/OpenLayers-js.html>`_
for more details.


Customizing the layout and the design
-------------------------------------

If you only want to customize the CSS, the easiest way to do it is to add a
link to an extra CSS to your *Areas* cf. :ref:`managing-areas`.

If you want to do larger changes in the layout and the style the (well named)
example_project can be customized to fit your needs. Each template file present
in the *chimere/templates* directory can be copied in your *myproject/templates*
directory and then modified.
You only need to copy files that you want to modify. These files are in
Django template language mainly made of pure HTML with some logic. Refer to
the `Django template documentation <https://docs.djangoproject.com/en/1.4/ref/templates/>`_
for more details.

