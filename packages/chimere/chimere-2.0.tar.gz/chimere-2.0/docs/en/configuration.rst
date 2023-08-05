.. -*- coding: utf-8 -*-

=============
Configuration
=============

:Author: Étienne Loks
:date: 2012-10-08
:Copyright: CC-BY 3.0

This document presents the first steps to configure your Chimère.
It has been updated for version 2.0.0.

Your session has to be initialised with these environment variables in
the Command Line Interface::

    CHIMERE_PATH=/srv/chimere # change with your installation path
    CHIMERE_LOCALNAME=mychimere # change with your local project name
    CHIMERE_APP_PATH=$CHIMERE_PATH/$CHIMERE_LOCALNAME


Once the application installed, there are a few simple steps to follow to
configure *your* Chimère.

Most of these steps are done in the web administration pages.

If you are not familiar with *Django-like* administration pages you can look
at the first paragraph of :ref:`administration` where it is presented.

To access these pages you have to identify with an account with *staff* and
*superuser* status.

A *superuser* account is created at the initialization of the database.

Configuring the Sites framework
-------------------------------

*Sites* framework allow you to serve the same content on different domains.
Most of you will probably use only one domain but this unique domain has to
be configured. This is done in the web administration interface in *Sites > Sites*.
You only need to change *example.com* by your domain name. If you forget to
do that, some functionalities such as RSS feeds will not work properly.

.. _managing-areas:

Managing areas
--------------

An *Area* is the base of your map. It defines:

* a name: a human readable label for this area,
* an associated URN (*not mandatory*): the name of the area as a web ressource.
  In practice, if the area is not the default area the URN is used at the end of
  the default URL to access to this area. This is not mandatory but necessary
  for each area that is not the default one,
* a welcome message (*not mandatory*): this message is displayed once a day per
  user arriving on the map,
* an order (to sort areas),
* an availability,
* a "*default*" state. The "*default*" area is viewed by default. Only one area
  can be the default: activating this state disables it on the possible other
  area with a default state,
* default checked categories (*not mandatory*),
* if categories are displayed dynamically. If dynamically is set, the end user
  only views categories which have items on the map section he is currently
  looking at,
* categories restriction (*not mandatory*): if no restriction is set all
  categories are available,
* an external CSS file (*not mandatory*): an URL to an external CSS file,
* restriction on the bounding box: if set to restricted, the end user can't pan
  outside the defined bounding box. Due to technical reasons of OpenLayers,
  there is at this time no restriction on the zoom,
* a map bounding box: this is the area to display when arriving on the map. If
  the area is restricted it will be the bounding box that restricts the end
  user. Hold the *control* key, click and drag to draw the bounding box,
* available layers (*not mandatory*: OSM Mapnik is used by default): OSM
  Mapnik render, OSM MapQuest render, OSM Transport Map render, OSM CycleMap are
  available by default. You can add new custom layers (cf.
  :ref:`managing-layers`).

*Areas* are customizable directly on the web administration interface in
*Chimere > Areas*.

As there is little chance that the default area should be appropriated for you, 
you'll have to set at least one default area.

Adding many areas can be a mean to show your map in different flavors.

Managing users
--------------

If you are not the only administrator/moderator of this Chimère installation
you have to create and manage account for the other users.

You can create a new *superuser* account with the Command Line Interface (CLI)::

    ./manage.py createsuperuser

User password can be changed with the CLI (useful if you have forgotten your
password)::

    ./manage.py changepassword username

*Users* are customizable directly on the web administration interface in
*Auth/User*.

To create a new account, simply click on the *Add* button near *Users*. Give a
name and a default password (the user can change it on his own later).

Then complete the other pieces of information.

Check the case: *Staff status* (or this user will not be able to log to the
administration website).

If this account is a new technical administrator, check *Superuser status* (this
user must be trustworthy!). Otherwise you'll have to give permissions to this
new user. It is easier not to add permission manually but to make this user
a member of a group.

Two types of default group are proposed: application administrator and
moderator.

Moderator are limited to an *Area* (they only see items that are inside the
bounding box). If a moderator manages many areas you'll have to select many
groups.

Detail of rights for default groups:

+-----------------------------------------+-------------------------+---------------------------+-----------+
|     Item (add/modify/delete on)         | Technical administrator | Application administrator | Moderator |
+=========================================+=========================+===========================+===========+
| User                                    |           yes           |            no             |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Group                                   |           yes           |            no             |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Property model                          |           yes           |            no             |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Import                                  |           yes           |            no             |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Layer                                   |           yes           |            no             |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| News                                    |           yes           |            yes            |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Area                                    |           yes           |            yes            |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Icon                                    |           yes           |            yes            |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Color/Color theme                       |           yes           |            yes            |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Category/Subcategory                    |           yes           |            yes            |    no     |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Point Of Interest                       |           yes           |            yes            |    yes    |
+-----------------------------------------+-------------------------+---------------------------+-----------+
| Route                                   |           yes           |            yes            |    yes    |
+-----------------------------------------+-------------------------+---------------------------+-----------+


Creating property models
------------------------

A basic installation of Chimère permits to associate a name, a category, a
description, dates, multimedia files, picture files, etc. for each geographic
item.

You may want to add more custom fields like phone number or opening hours. For
that all you have to do is to add a new property model (*Chimere/Property
model*).

The administration page asks you for:

* a name,
* an order (to sort properties),
* an availability to the end user (this can be used to set hidden properties),
* a mandatory status,
* the categories the property applies to (if no categories selected it applies
  to all),
* the type: text, long text, password or date.

To make this property available it is necessary to reload your web server (the
property is cached).

All forms are then automatically updated with this new field.

If you don't want to allow add and modification of properties you can disable
this form by setting CHIMERE_HIDE_PROPERTYMODEL to *True* in your
*local_settings.py* file.

