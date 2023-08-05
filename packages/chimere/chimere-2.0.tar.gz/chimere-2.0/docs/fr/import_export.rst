.. -*- coding: utf-8 -*-

=============
Import/export
=============

:Author: Étienne Loks
:date: 2012-11-28
:Copyright: CC-BY 3.0

Ce document présente les fonctions d'import et d'export de Chimère.
Ce document a été mis à jour pour la version 2.0.0 de Chimère.

.. _importing:

Import
------

Dans Chimère, le mécanisme d'import est basé sur les objets **Import**. Ces
objets sont stockés dans une base de données pour garder trace des imports et
pour faciliter la ré-importation depuis une même source. En fait, si cela est
possible, la mise à jour de données depuis un même type de source est gérée, de
préférence à une ré-importation.

.. Note::
    La possibilité de réaliser de telles mises à jour est conditionnée à
    l'existence d'un identifiant unique pour chaque objet de la source.

Pour ajouter un objet **Import**, vous devez aller dans *Chimere > Imports* puis
cliquer sur **Ajouter**.

Après cela, vous aurez à sélectionner votre type de source. Le formulaire
suivant dépend de ce type de source.

Champs communs à tous les types de source
*****************************************

- **Nom par défaut** : si aucun nom ne peut être trouvé dans la source pour ce
  nouvel objet le nom par défaut sera utilisé. Si ce champ est vide le nom de
  la catégorie associée sera utilisée.
- **SRID** : Chimère tente d'identifier automatiquement le système de coordonnées
  utilisé par la source. Mais parfois l'information n'est pas présente ou ne
  peut pas être devinée (par exemple un fichier Shapefile qui utilise un fichier
  proj non standard). Dans ce cas, Chimère utilise WGS84 par défaut (latitude et
  longitude). Si vous avez des problèmes avec la localisation des éléments vous
  devez probablement mettre ici le `SRID <https://en.wikipedia.org/wiki/SRID>`_
  correspondant au système de coordonnées de votre source.
- **Écraser les données existantes** : par défaut quand les données ont été
  mises à jour à la fois sur la source externe et sur votre source externe un
  nouvel élément est créé et a à être rapproché avec le :ref:`formulaire de
  gestion des modifications <managing-modified>`. Si vous ne souhaitez pas avoir
  à faire ce rapprochement et alors écraser les données existantes avec les
  données de la source externe, cochez cette option.
- **Origine** : si non nul, ce champ va être associé à chaque élément importé
  afin d'identifier facilement d'où l'élément provient. Pour les imports OSM
  la source est ajoutée automatiquement.
- **Licence** : si non nul, ce champ va être associé à chaque élément importé
  afin d'identifier facilement la licence de l'élément. Pour les imports OSM
  la licence est ajoutée automatiquement.
- **Sous-catégories (obligatoire)** : les sous-catégories sélectionnées seront
  associées automatiquement aux nouveaux éléments importés.


Import KML
**********

.. image:: static/chimere_admin_import_KML.png


- **Adresse Web / fichier source (obligatoire)** : votre fichier KML peut être
  local ou distant. Vous avez à remplir un des deux champs.
- **Filtre**: si vous souhaitez importer seulement un dossier (**Folder**) du
  fichier KML mettez son nom dans ce champ.
- **Fichier zippé**: si votre source est un fichier KMLZ (un fichier KML zippé),
  cochez cette case.

Import Shapefile
****************

.. image:: static/chimere_admin_import_shapefile.png


- **Adresse Web / fichier source (obligatoire)** : votre fichier shapefile peut
  être local ou distant. Vous avez à remplir un des deux champs.
- **Fichier zippé**: seuls les fichiers shapefile zippés sont acceptés aussi
  cette case devrait être cochée.

Import GeoRSS
*************

Simple GeoRSS et W3C GeoRSS sont gérés.

.. image:: static/chimere_admin_import_georss.png

- **Adresse Web (obligatoire)**: seul les flux GeoRSS distant sont gérés.

Import CSV
**********

Le format du fichier CSV (nombre et ordres des colonnes) géré par Chimère
varie en fonction des modèles de propriété que vous avez utilisé sur votre
instance Chimère.
Aussi, il est recommandé dans un premier temps de faire un export CSV de
quelques éléments.
Le format du fichier CSV exporté sera compatible avec Chimère pour l'import.


En tout cas à cause des champs géographiques ce format n'est pas très
pratique pour l'ajout de nouveau contenu mais peut s'avérer utile pour les
mises à jour d'information.

.. Warning::
   Si vous souhaitez mettre à jour des données existantes avec cet import, à
   moins que vous sachiez éditer du WKT ne modifiez **pas** la colonne qui
   concerne la géométrie de l'élément.

.. image:: static/chimere_admin_import_CSV.png

- **Adresse Web/fichier source (obligatoire)** : votre fichier CSV peut être
  distant ou local. Vous avez à remplir un des deux champs.

.. _osm-import:

Import OpenStreetMap
********************

.. image:: static/chimere_admin_import_OSM.png

Pour importer depuis OSM, Chimère utilise l'API XAPI d'OSM.

- **Adresse Web (obligatoire)**: l'URL XAPI à utiliser pour importer. Ce champ
  doit être rempli par défaut. Par défaut le serveur MapQuest est utilisé car
  il semble le plus robuste. Si vous avez des problèmes avec l'import de données
  OSM, vérifiez la disponibilité du serveur utilisé et le cas échéant changez
  le.
- **Filtre sur zone (obligatoire)**: dessinez la section de carte à utiliser
  pour votre import OSM.
- **Filtre sur types (obligatoire)**: choisissez si vous souhaitez importer des
  routes ou des nœuds.
- **Filtre sur les clé/valeur (obligatoire)**: choisissez la paire clé/valeur
  à utiliser pour filtrer les données OSM. Un lien vers la `page de « Map
  features » OSM <https://wiki.openstreetmap.org/wiki/Map_Features>`_ est
  fourni pour vous aider à trouver les valeurs adaptées.
- **Bouton de rafraîchissement**: ce bouton convertit vos choix en arguments
  XAPI adaptés. N'oubliez pas de presser sur ce bouton avant de valider le
  formulaire.

Importer
********

Une fois que le nouvel objet *Import* est créé, sélectionnez le dans la liste
des objets, choisissez *Importer* et valider.

L'import doit se dérouler normalement. Dans le cas contraire, un message
d'erreur explicite doit s'afficher dans la colonne *État* de votre import.

Vous pouvez aussi lancer vos imports en ligne de commande (idéal pour les
travaux à mettre dans la table *cron*). Dans le répertoire du projet, il est
juste nécessaire de lancer la commande ::

    ./manage.py chimere_import <import_id>

- *import_id* est l'identifiant de l'import

Si vous lancez l'import en ligne de commande sans l'identifiant d'import, la
liste des imports disponibles est affichée et vous pouvez alors en choisir un.

.. _manage-imported-data:

Gérer les données importées
***************************

Tous les nouveaux éléments importés ont l'état **Importé**. Pour que ceux-ci
soient disponible sur la carte, il est nécessaire de les valider. Si vous
ne souhaitez pas afficher certains éléments plutôt que de les supprimer, il est
recommandé de les mettre à l'état **Désactivé**. Ainsi lors de la prochaine
mise à jour depuis la source, ceux-ci resteront désactivés plutôt que
d'apparaître comme nouveaux éléments.

.. Warning::
   Soyez vigilants avec les doublons entre les données existantes et les données
   importées. C'est particulièrement important si vous souhaitez exporter vos
   données vers OSM.

Export
------

Exporter vers CSV/KML/Shapefile
*******************************

Depuis les :ref:`listes d'éléments géographiques <geographic-items-management>`
vous pouvez exporter directement vers le format choisi.
Tout ce que vous avez à faire c'est de sélectionner les éléments que vous
souhaitez exporter, choisir l'action appropriée dans la liste d'action et de
valider.

Vous pouvez aussi lancer les exports depuis la ligne de commande (idéal pour les
travaux à mettre dans la table *cron*). Dans le répertoire du projet, vous avez
juste à lancer ::

    ./manage.py chimere_export <subcategory_id> <CSV|KML|SHP> \
                               <marker|route> <filename>

- *subcategory_id* est l'identifiant de la sous-categorie choisie ;
- *CSV|KML|SHP* est le format choisi ;
- *marker|route* est pour obtenir points d'intérêts (marker) ou trajets
  (route) ;
- *filename* est le nom du fichier de sortie

Si vous lancez la commande sans arguments il vous sera demandé les choix à faire
pour votre export.


Exporter vers OSM
*****************

.. Warning::
   Si vous n'êtes pas sûr de ce que vous êtes entrain de faire avec les exports
   vers OSM : **ne le faites pas !** C'est vraiment important de ne pas
   plaisanter avec les données des autres.

.. Note::
    Seuls les exports des nœuds OSM sont gérés.

Les exports ne sont pas aussi facile à gérer que les autres exports. Tout
d'abord (si cela n'est pas déjà fait) vous avez à définir un import OSM
(:ref:`regarder dessus <osm-import>` pour plus de détail). Cela permettra de
déterminer :

- la zone géographique concernée par votre export ;
- la clé/valeur à ajouter à vos éléments (nouveaux ou mis à jour) ;
- les sous-catégories concernées par cet export. Si vous pensez que certains
  éléments dans ces sous-catégories ne devraient pas être dans la base de
  données OSM (car ils ne sont pas pertinents ou à cause de question de licence)
  marquez les préalablement comme **À ne pas exporter vers OSM** dans les
  *champs d'imports* des :ref:`formulaires concernant les éléments géographiques
  <geographic-items-management>`.


L'export vers OSM dans Chimère est fait de sorte à être le plus
conservateur possible par rapport à la base de données OSM. C'est pour cela
qu'avant tout export, un import est fait. Si le nouvel import a des données
mises à jour, il est nécessaire de retraiter les nouvelles données importées
avant de faire un export (cf. :ref:`gérer les données importées
<manage-imported-data>`).

Pour lancer un export sélectionnez l'objet *Import* approprié dans la liste
des imports. Ensuite sélectionnez l'action **Exporter vers OSM** et validez.
Puis on vous demande votre identifiant OSM, votre mot de passe OSM et l'API
que vous souhaitez utiliser. Si vous comptez faire des exports régulièrement
avec Chimère, il est recommandé de créer un compte spécifique pour cela.
L'API de test est disponible pour faire des tests d'export. Si vous souhaitez
utiliser l'API de test, vous aurez à créer un compte spécifique sur la
plateforme de test.

.. Warning::
   Les données sur la plateforme de test ne sont pas synchronisées avec la
   plateforme principale. Vous n'aurez pas les mêmes données que celles celles
   importées avec XAPI.

Une fois que tous ces champs sont remplis, vous pouvez (enfin !) lancer
l'export.

Quand vous exportez, des couples clés/valeurs sont automatiquement ajoutés/mis à
jour dans la base de données OSM :

- *name*: obtenu depuis le nom de l'élément dans Chimère ;
- *source*: pour identifier Chimère comme une source.
