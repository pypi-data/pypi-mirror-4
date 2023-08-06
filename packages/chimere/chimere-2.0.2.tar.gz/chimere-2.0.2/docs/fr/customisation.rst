.. -*- coding: utf-8 -*-

================
Personnalisation
================

:Auteur: Étienne Loks
:date: 2012-11-29
:Copyright: CC-BY 3.0

Ce document présente la personnalisation de Chimère.
Ce document a été mis à jour pour la version 2.0.0 de Chimère.

.. _managing-layers:

Gestion des calques
-------------------

Il y a différents calques disponibles par défaut dans Chimère (OSM Mapnik, OSM
Mapquest, OSM Transport map, OSM Cyclemap). Vous pouvez ajouter d'autres calques
en utilisant les pages d'administration de Chimère.

Le nouveau calque est défini en utilisant une chaîne de code Javascript adéquate
de la bibliothèque  `Openlayers <http://openlayers.org/>`_. Ce code Javascript
doit être une instance de *Openlayers Layer*, sans point virgule final.

Par exemple définir un calque Bing peut être fait avec un code de ce type : ::

    new OpenLayers.Layer.Bing({
                name: "Aerial",
                key: "my-bing-API-key",
                type: "Aerial"})


Référez vous à la `documentation de l'API Openlayers
<http://dev.openlayers.org/releases/OpenLayers-2.12/doc/apidocs/files/OpenLayers-js.html>`_
pour plus de détail.


Personnaliser l'agencement et le design
---------------------------------------

Si vous souhaitez simplement améliorer la feuille de style CSS, le plus simple
est d'ajouter un lien vers une feuille de style supplémentaire dans vos *Zones*
(cf. :ref:`managing-areas`).

Si vous souhaitez faire des changements plus importants dans l'agencement et la
présentation, le projet *example_project* peut être personnalisé pour
correspondre à vos besoins. Chaque fichier de patron de page présent dans le
dossier *chimere/templates* peut être copié dans votre dossier
*monprojet/templates* puis modifié.

Il est juste nécessaire de copier les fichiers que vous souhaitez modifier.
Ces fichiers sont écrits dans le langage de patron Django principalement composé
de HTML avec des éléments de logique. Référez vous à la `documentation des
patrons Django <https://docs.djangoproject.com/en/1.4/ref/templates/>`_ pour
plus de détails.

