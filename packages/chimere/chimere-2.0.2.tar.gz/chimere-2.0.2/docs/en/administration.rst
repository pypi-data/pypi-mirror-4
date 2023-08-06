.. -*- coding: utf-8 -*-
.. _administration:

==============
Administration
==============

:Author: Étienne Loks
:date: 2012-11-28
:Copyright: CC-BY 3.0

This document presents the administration of Chimère.
It has been updated for version 2.0.0.


Administration pages presentation
---------------------------------

Administration pages are accessible at: http://where_is_your_chimere/admin/

Don't forget the ending slash in the URL.

Identification
**************

First of all, you'll have to identify yourself with the login and password
provided.

.. image:: static/chimere_admin_00.png


Main page
*********

Once authentified you'll have access to the main admin page.

It looks like this:

.. image:: static/chimere_admin_01.png

#. links to this **Documentation**, to the **Change password** form and to
   **Log out**,
#. the list of recent actions made with this account,
#. an application title, most of your action will be in the **Chimere**
   application,
#. an item inside the application. From these pages you can **Add** a new item or
   consult/**Change** items. The **Add** link leads to the new `Item form`_. The
   **Change** link leads to the `Item list`_. The `Item list`_ is also available
   by clicking on the item label.


Item list
*********

.. image:: static/chimere_admin_02.png

#. path in the admin site. This is a convenient shortcut to come back to the
   main page,
#. link to create a new item from the item list,
#. search items by words (not available for all item types),
#. this filter box permits to filter current entries with some criteria (not
   available for all type of items),
#. the header of the table is clickable. Clicking on an header sorts the items by
   this header (ascending or descending). Multiple header sort is possible (the
   number on the right of the header explains the sorting order),
#. each item can be checked (for applying an action) or selected (by clicking on
   the first column) to see the detail and edit or delete it.

Item form
*********

.. image:: static/chimere_admin_03.png

#. fields for the selected item (or blank if it is a new item) are displayed in
   this form. A few fields are read-only and another few are hidden. Mandatory 
   fields have their label in bold. Changes on these fields are only effective 
   once the form is submitted.
#. for some items there are associated sub-items. These associated items can be
   modified in this form. If there are many sub-items associated for the current
   item, they can be ordered by drag and drop.
#. the form has to be validated by one of these action buttons. They are
   self-explanatory.

Status
******

*Status* is a property attached to each geographic item in Chimère. To
administrate efficiently Chimère you need to understand the mean of each status.

- **Submitted**: Status of a new item freshly proposed by an end user. This item
  is not visible on the map.
- **Available**: Status of an item visible on the map.
- **Disabled**: Status of a discarded item.
- **Modified**: Status of an amendment proposed by an end-user.
- **Imported**: Status of a newly imported item. Import and export operations
  need that all items with *imported* status are treated (validated, disabled
  or deleted).


Managing news
-------------

A news system is available.
All you have to to do is to click on the **Add** button near News.
For each news you have to provide a name and a content. The content can contain
HTML tags.
The availability is set with a checkbox.

Creating categories/subcategories
---------------------------------

Before adding categories you have to set some icons. These icons appear on the
map and in the categories' box on the main map.
Be careful to resize correctly your icons. Indeed the icon will be presented at
their real size on the map.
To add icons: the **Add** button near Icons.

The website http://mapicons.nicolasmollet.com/ allow to easily generate map
icons.

Categories are in fact only containers for subcategories. You'll have to provide
only a name and an order.
To add categories: the **Add** button near categories (quite clear now, isn't
it?).

Fields of subcategories are: an associated category, a name, an icon, an order,
a color and an element type.
These fields are mainly quite self- explanatory.
The color is used to draw routes (if this subcategory contains routes). If it a
basic color it can be set with the English name (for instance: *red*, *blue*,
*yellow* or *purple*) otherwise you can put the HTML RVB code (for instance
*#9227c9*).
The element type is the type of element that the subcategory can contain: POI, route
or both.

.. _geographic-items-management:

Editing or moderating items
---------------------------

The moderation step is quite simple. It works the same with POIs and routes.
The moderator can access to all POIs (or routes) by clicking on them on the
list.

A search field is available to search by name but the more interesting is to
filter POIs (or route) by state and by subcategory.

There are some actions available in the action list:

- **Delete**: to delete selected items. A confirmation step is displayed,
- **Validate**: to set the status *Available* to selected items,
- **Disable**: to set the status *Disabled* to selected items. This is useful to
  keep items you don't want to be exposed on the map,
- **Managed modified items**: to manage the amendment made by end users on the
  main site (cf. :ref:`managing-modified`). Modified item has to be treated
  one by one,
- **Export to...**: to export selected item to the selected format.


To modify an item, classically you have to click on its name.
Then you access to a form to freely modify the item.

.. image:: static/chimere_admin_modify_item.png

In this form there are all data available to the end user form plus some extra
fields.

- The *Import fields* only make sense with data imported from an external
  source or for data to be exported to OSM (cf. the :ref:`import section
  <importing>` of this documentation),
- *Associated items fields* are read-only fields that list items associated to
  the current one (for example the reference item of an amendment or an associated 
  file of a route).

Associated multimedia items are at the bottom of the form. You can freely add,
change items and change their order with drag and drop.

Don't forget to validate your change with one of the **Save** buttons at the
bottom of the form (it is easily forgotten when you change multimedia items).

If an item is not relevant the **Delete** button enables to remove it.

.. _managing-modified:

Managing end user amendment/imported item modified locally
----------------------------------------------------------

Amendment can be proposed on the main site by end-users.
In Chimère an amendment is a new item with the status **Modified** and with a
link to the reference item modified.

You can also have imported items which have been modified both locally and on
the external source. The new version from the external source has the status
**Imported** and have a link to the reference item.

.. Note::
   If you are logged as an administrator and make changes on the map with the
   end user form they will be directly validated.


A special form has been developed to facilitate the processing of these
modified items.

You can access to this special form with the action *Managed modified items*.

.. image:: static/chimere_admin_modified_management.png

This form is a table with three columns:

#. The first column displays the information for the reference item,
#. The second column displays the information proposed by the submitter,
#. The third column is a list of checkboxes. For each row checked, after the
   validation, the value of the modified item will replace the value of the
   reference item.

.. Note::
   To reject all modifications validate the form with no checkbox checked.
