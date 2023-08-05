.. -*- coding: utf-8 -*-
.. _administration:

==============
Administration
==============

:Auteur: Étienne Loks
:date: 2012-11-29
:Copyright: CC-BY 3.0

Ce document présente l'administration de Chimère.
Il a été mis à jour pour la version 2.0.0 de Chimère.

Présentation des pages d'administration
---------------------------------------

Les pages d'administration sont accessibles à l'adresse :
http://where_is_your_chimere/admin/

N'oubliez pas la barre oblique (slash) à la fin de l'adresse.

Identification
**************

Tout d'abord vous avez à vous identifier avec l'identifiant et le mot de
passe fournis.

.. image:: static/chimere_admin_00.png


Page principale
***************

Une fois identifié, vous avez accès à la page principale d'administration.

Cela s'affiche ainsi :

.. image:: static/chimere_admin_01.png

#. lien vers cette **Documentation**, vers le formulaire de **Changement de mot
   de passe** et la déconnexion ;
#. la liste des actions récemment faites avec ce compte ;
#. un titre d'application, la plupart des actions vont se faire dans
   l'application **Chimere** ;
#. un élément à l'intérieur de l'application. Depuis ces pages, vous pouvez
   *Ajouter* un nouvel élément ou consulter/**Changer** des éléments. Le lien
   **Ajouter** conduit au `Formulaire des éléments`_. Le lien **Modifier**
   conduit à la `Liste des éléments`_. La `Liste des éléments`_ est également
   disponible en cliquant sur le libellé de l'élément.


Liste des éléments
******************

.. image:: static/chimere_admin_02.png

#. chemin dans le site d'administration. C'est un raccourci pratique pour
   revenir à la page principale.
#. lien pour créer un nouvel élément depuis la liste des éléments.
#. recherche des éléments par mot (n'est pas disponible pour tous les types
   d'éléments).
#. cette boite permet de filtrer les entrées actuelles avec des filtres (n'est
   pas disponible pour tous les types d'éléments)
#. les en-têtes de cette table sont cliquables. Cliquer sur une en-tête permet
   de trier les éléments de manière ascendante et descendante. Un tri multi-en-tête
   est possible (le nombre à droite de l'en-tête indique l'ordre de prise en
   compte dans le tri).
#. chaque élément peut être coché (pour lui appliquer une action) ou sélectionné
   (en cliquant sur la première colonne) pour voir son détail et éventuellement
   le modifier ou le supprimer.

Formulaire des éléments
***********************

.. image:: static/chimere_admin_03.png

#. les champs pour l'élément sélectionné (ou vide si c'est un nouvel élément)
   sont affichés dans ce formulaire. Parfois certains champs sont en lecture
   seule et d'autres sont cachés. Les champs obligatoires ont leur intitulé en
   gras. Les changements sur ces champs ne sont effectifs qu'une fois le
   formulaire validé.
#. pour certains éléments il y a des sous-éléments associés. Ces sous-éléments
   peuvent être modifiés directement dans ce formulaire. Lorsque plusieurs
   sous-éléments sont associés à un élément, ils peuvent être réagencés par
   glisser-déposer.
#. le formulaire doit être validé par un de ces boutons. Ils parlent d'eux-même.

États
*****

Les *États* sont des propriétés rattachées à chaque élément géographique dans
Chimère. Pour administrer Chimère efficacement il est nécessaire de comprendre
chacun de ces états.

- **Proposé**: État d'un élément nouvellement proposé par un utilisateur. Cet
  élément n'est pas visible sur la carte.
- **Disponible**: État d'un élément visible sur la carte.
- **Désactivé**: État d'un élément écarté.
- **Modifié**: État d'une proposition de modification d'un élément par un
  utilisateur.
- **Importé**: État d'un élément nouvellement importé. Les opérations d'import
  et d'export nécessitent que tous les éléments avec l'état *importé* soient
  traités (validés, désactivés ou supprimés).


Gestion des nouvelles
---------------------

Un système de nouvelles est disponible.
Tout ce que vous avez à faire est de cliquer sur le bouton *Ajouter* à côté de
*Nouvelles*.
Pour chaque nouvelle il est nécessaire de fournir un nom et un contenu. Le
contenu peut contenir des balises HTML.
La disponibilité est gérée avec une case à cocher.

Création de catégories/sous-catégories
--------------------------------------

Avant l'ajout de catégories, il est nécessaire de définir des icônes. Ces icônes
apparaissent sur la carte et sur la boîte contenant les catégories sur la carte
principale.
Faites attention de bien redimensionner vos icônes. En effet les icônes vont
être présentées à leur taille réelle sur la carte.
Pour ajouter des icônes : cliquez sur le bouton **Ajout** à côté de *Icônes*.

Le site http://mapicons.nicolasmollet.com/ permet de générer facilement des
icônes adaptées à un usage dans Chimère.

Les catégories sont en fait des conteneurs à sous-catégories. Il est juste
nécessaire de fournir nom et ordre d'affichage.
Pour ajouter des catégories : cliquez sur le bouton **Ajout** près des
catégories.

Les champs concernant les sous-catégories sont : un nom, une icône, un ordre,
un thème de couleur et un type d'élément.
La plupart des champs parlent d'eux-mêmes.
Les thèmes de couleurs sont composés de plusieurs couleurs.
Les couleurs sont utilisées pour le tracé des trajets (si la sous-catégorie
contient des trajets). Si c'est une couleur de base, cela peut être défini
par le nom en anglais (par exemple *red* pour rouge, *blue* pour bleu,
*purple* pour violet) sinon vous pouvez donner le code couleur HTML RVB
(par exemple *#9227c9*).
Le type d'élément est le type d'élément que la sous-catégorie peut contenir :
points d'intérêts, trajets ou les deux.

.. _geographic-items-management:

Édition/modération des éléments
-------------------------------

L'étape de modération est relativement simple. Elle fonctionne de la même
manière avec les points d'intérêt ou avec les trajets.
Le modérateur accède classiquement aux points d'intérêts (ou trajets) en
cliquant sur leur nom dans la liste d'éléments.

Un champ de recherche est disponible pour rechercher par nom mais il est
généralement plus intéressant de filtrer par état et sous-catégories.

Il y a un certain nombre d'action disponible.

- **Supprimer** pour supprimer les éléments sélectionnés. Une étape de
  confirmation est affichée.
- **Valider** pour donner le status *Disponible* aux éléments sélectionnés.
- **Désactiver** pour donner le status *Désactivé* aux éléments sélectionnés.
  C'est particulièrement utile pour garder des éléments que vous ne voulez
  pas voir apparaître sur la carte mais conserver en base de données.
- **Gérer les éléments modifiés** pour gérer les propositions de modification
  par les utilisateurs sur le site principal (cf. :ref:`managing-modified`).
  Les éléments modifiés ne peuvent être traités qu'un par un.
- **Export en...** pour exporter les éléments sélectionnés vers le format
  sélectionné.


Pour modifier un élément, classiquement, vous cliquez sur son nom pour accéder
ensuite à un formulaire pour modifier librement l'élément.

.. image:: static/chimere_admin_modify_item.png

Sur ce formulaire il y a tous les éléments disponibles à l'utilisateur plus
quelques champs supplémentaires.

- Les champs *Imports* ne sont pertinent que pour les données importées depuis
  une source externe ou pour les données destinées à être exportées vers OSM
  cf. à la :ref:`section import <importing>` de cette documentation.
- Les *Éléments associés* sont des champs en lecture seule qui listent les
  éléments associés à l'élément courant (élément de référence d'une
  modification, fichier associé à un trajet).


Les éléments multimédias sont listés à la fin du formulaire. Vous pouvez
librement ajouter, modifier, changer l'ordre (avec du glisser-déposer) de ces
éléments.

Si un élément n'est pas pertinent, le bouton **Supprimer** permet de le
supprimer.

.. Warning::
   N'oubliez pas de valider vis changements avec un des boutons d'enregistrement
   disponibles à la fin du formulaire (notamment il est assez facile d'oublier
   de confirmer les changements faits aux éléments multimédias).

.. _managing-modified:

Gérer les modifications des utilisateurs/les éléments importés ayant des modifications locales
----------------------------------------------------------------------------------------------

Des propositions de modification peuvent être faits sur le site principal par
les utilisateurs.

Dans Chimère, une proposition de modification est un nouvel élément avec l'état
**Modifié** qui dispose d'un lien vers l'élément de référence.

Vous pouvez avoir aussi des éléments importés qui ont à la fois des
modifications locales et sur la source externe. La nouvelle version de la source
externe a l'état **Importé** et un lien vers l'élément de référence.

.. Note::
   Si vous êtes identifié en tant qu'administrateur et que vous faites des
   changements sur la carte avec le « formulaire utilisateur » les changements
   vont être directement pris en compte.

Un formulaire spécifique a été développé pour faciliter le traitement de ces
éléments modifiés.

Vous pouvez accéder à ce formulaire spécifique avec l'action *Gérer les éléments
modifiés*.

.. image:: static/chimere_admin_modified_management.png

Ce formulaire est un tableau à 3 colonnes.

#. La première colonne affiche les informations de l'élément de référence.
#. La seconde colonne affiche les informations que propose l'utilisateur.
#. La troisième colonne est une liste de cases à cocher. Après validation, pour
   chaque ligne cochée, la valeur de l'élément modifié remplacera la valeur de
   l'élément de référence.

.. Note::
   Pour rejeter toutes les modifications proposées, validez le formulaire sans
   cocher aucune case.
