.. -*- coding: utf-8 -*-

=============
Configuration
=============

:Auteur: Étienne Loks
:date: 2012-11-29
:Copyright: CC-BY 3.0

Ce document présente l'installation de Chimère.
Il a été mis à jour pour la version 2.0.0 de Chimère.

Votre session doit être initialisée avec ces variables d'environnement
en ligne de commande : ::

    CHIMERE_PATH=/srv/chimere # changez avec votre répertoire d'installation
    CHIMERE_LOCALNAME=mychimere # changez avec le nom de votre projet
    CHIMERE_APP_PATH=$CHIMERE_PATH/$CHIMERE_LOCALNAME


Une fois l'application installée, il y a un certain nombre d'étapes à suivre
pour configurer *votre* Chimère.

La plupart de ces étapes sont faites dans les pages web d'administration.

Si vous n'êtes pas familiarisé avec les pages d'administration de *type
Django* vous pouvez dès maintenant regarder le premier paragraphe de
l':ref:`administration` où elles sont présentées.

Pour accéder à ces pages vous avez à vous identifier avec un compte ayant
pour état *équipe* ou *super-utilisateur*.

Un compte *super-utilisateur* est créé à l'initialisation de la base de données.

Configurer le framework Sites
-----------------------------

Le framework *Sites* vous permet de servir le contenu pour différents domaines
Internet. La plupart des installations serviront le contenu pour un seul domaine
mais ce domaine unique doit être configuré.

Pour cela allez dans les pages web d'administration *Sites > Sites*.
Vous avez juste à changer *example.com* par votre nom de domaine. Si vous
oubliez de faire cela, quelques fonctionnalités comme les flux RSS ne
fonctionneront pas correctement.

.. _managing-areas:

Gérer les zones
---------------

Une zone est la base de votre carte. Pour une zone il est défini :

* un nom : un libellé pour cette zone ;
* une URN associée (*facultatif*) : le nom de la zone en tant que ressource
  Web. En pratique si la zone définie n'est pas celle par défaut, elle est
  utilisée à la fin de l'adresse Web de base pour pouvoir accéder à cette zone.
  Ce n'est pas obligatoire mais nécessaire en pratique pour chaque zone qui
  n'est pas celle par défaut ;
* un message par défaut (*facultatif*) : ce message est affiché une fois par
  jour par utilisateur consultant la carte ;
* un ordre (pour trier les zones) ;
* une disponibilité ;
* un état « *par défaut* ». La zone *par défaut* est vue par défaut. Une seul
  zone peut être *par défaut* : activez cet état sur une zone le désactive sur
  toutes les autres ;
* des catégories cochées par défaut (*facultatif*) ;
* si les catégories sont affichées dynamiquement. Si les catégories sont
  affichées dynamiquement, l'utilisateur ne voit seulement que les catégories
  qui ont des éléments sur la portion de carte actuellement à l'écran ;
* des restrictions sur les catégories (*facultatif*): si aucune restriction
  n'est définie, toutes les catégories sont disponibles ;
* une feuille de style CSS externe (*facultatif*) : une adresse Web qui pointe 
  vers une feuille de style CSS externe ;
* une restriction à la portion de carte : si coché, l'utilisateur ne pourra
  pas faire glisser la carte en dehors de la portion de carte. À cause de
  limitations de la bibliothèque OpenLayers utilisée par Chimère, il n'y a pas
  de restriction sur le zoom ;
* une portion de carte : c'est la zone qui sera affichée par défaut en arrivant
  sur la carte. Si la restriction sur une portion de carte est activée, la
  restriction portera sur cette portion. Laissez appuyée la touche *Control*,
  cliquez et glissez pour dessiner la portion de carte choisie.
* calques disponibles (*facultatif* : OSM Mapnik est utilisé par défaut): les
  rendus OSM Mapnik, OSM MapQuest, OSM Transport Map, OSM CycleMap sont
  disponibles par défaut. Vous pouvez ajouter de nouveaux calques (cf.
  :ref:`managing-layers`).

Les *Zones* sont personnalisables directement depuis l'interface
d'administration dans *Chimere > Zones*.

Comme il y a peu de chance que la zone définie par défaut vous convienne, il
sera au minimum nécessaire de définir une zone par défaut.

Ajouter plusieurs zones peut être un moyen d'afficher vos données de différentes
manières.

Gestion des utilisateurs
------------------------

Si vous n'êtes pas le seul administrateur/modérateur de cette installation de
Chimère vous aurez à créer et gérer des comptes pour les autres utilisateurs.

Vous pouvez créer un nouvel administrateur en ligne de commande : ::

    ./manage.py createsuperuser

Les mots de passe peuvent être changés en ligne de commande (utile si vous
avez oublié votre mot de passe) : ::

    ./manage.py changepassword username

Les *Utilisateurs* sont directement éditables depuis les pages d'administration
au niveau de la section *Auth/Utilisateur*.

Pour créer un nouveau compte, cliquez simplement sur le bouton *Ajouter* à côté
de *Utilisateur*. Donnez un nom et un mot de passe (l'utilisateur pourra changer
son mot de passe plus tard).

Ensuite complétez les autres informations.

Cochez la case : *Statut équipe* (ou cet utilisateur ne sera pas capable
d'accéder aux pages d'administration).

Si ce compte est un nouvel administrateur technique, cochez la case *Statut
superutilisateur* (cet utilisateur doit être digne de confiance !). Sinon
vous allez devoir donner des permissions à ce nouvel utilisateur. Plutôt que
d'assigner manuellement des permissions aux utilisateurs, il est plus simple
de leur affecter un groupe avec des permissions pré-définies.

Deux types de groupe sont proposés par défaut : les administrateurs de
l'application et les modérateurs.

Les groupes de modérateurs ont des droits limités à une seule zone (le nom
du groupe est *Nom_de_zone modération*). Ils ne voient que les éléments
qui concernent leur zone. Un utilisateur pouvant faire partie de plusieurs
groupes, il peut modérer plusieurs zones.


Détails des droits pour les groupes par défaut :

+------------------------------------------+--------------------------+---------------------------------+------------+
| Élément (ajout/modification/suppression) | Administrateur technique | Administrateur de l'application | Modérateur |
+==========================================+==========================+=================================+============+
| Utilisateur                              |            Oui           |               Non               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Groupe                                   |            Oui           |               Non               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Modèle de propriété                      |            Oui           |               Non               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Import                                   |            Oui           |               Non               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Calque                                   |            Oui           |               Non               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Nouvelles                                |            Oui           |               Oui               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Zone                                     |            Oui           |               Oui               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Icône                                    |            Oui           |               Oui               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Couleurs/thème de couleur                |            Oui           |               Oui               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Catégorie/Sous-catégorie                 |            Oui           |               Oui               |     Non    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Point d'intérêt                          |            Oui           |               Oui               |     Oui    |
+------------------------------------------+--------------------------+---------------------------------+------------+
| Trajet                                   |            Oui           |               Oui               |     Oui    |
+------------------------------------------+--------------------------+---------------------------------+------------+


Créer des modèles de propriété
------------------------------

Une installation de base de Chimère permet d'associer un nom, des catégories,
une description, des dates, des fichiers multimédias, des fichiers d'image
à chaque élément géographique.

Vous souhaitez peut-être des champs personnalisés tels que des numéros de
téléphone ou des horaires d'ouverture. Pour cela, il suffit d'ajouter un nouveau
modèle de propriété (*Chimere/Modèle de propriété*).

La page d'administration vous demande : 

* un nom ;
* un ordre (pour ordonner les propriétés entre elles) ;
* une disponibilité pour l'utilisateur (cela peut être utilisé pour associer
  des propriétés cachées) ;
* un état « Obligatoire » qui oblige à remplir ce champ dans les formulaires ;
* les catégories auxquelles associer cette propriété (si aucune catégorie n'est
  sélectionnée, la propriété est disponible pour toutes les categories) ;
* le type : texte, texte long, mot de passe ou date.

.. Warning::
    Pour rendre cette propriété disponible, il est nécessaire de recharger le
    serveur Web (les propriétés sont mis en cache).

Les formulaires sont alors automatiquement mis à jour avec ce nouveau champ.

En tant qu'administrateur, si vous ne souhaitez pas rendre disponible l'ajout
ou la modification des propriétés, vous pouvez désactiver la gestion des modèles
de propriété en mettant *CHIMERE_HIDE_PROPERTYMODEL* à la valeur *True* dans
votre fichier *local_settings.py*.
