.. -*- coding: utf-8 -*-

===========
Mise à jour
===========

:Auteur: Étienne Loks
:date: 2012-11-29
:Copyright: CC-BY 3.0

Ce document présente la mise à jour de Chimère.
Il a été mis à jour pour la version 2.0.0 de Chimère.

.. Warning::
   Avant toute mise à jour faites une sauvegarde de la base de données et de
   tous vos fichiers d'installation (en particulier si vous avez fait des
   changements sur ceux-ci).

La procédure de migration nécessite une connaissance de base de Git et de la
ligne de commande Linux. Ce n'est *pas* une procédure facile. Un travail est en
cours pour faciliter les mises à jour des futures versions de Chimère (>2.0).

Si plusieurs versions de Chimère ont été publiées depuis votre installation,
vous devez répéter toutes les étapes de mise à jour.
Par exemple pour mettre à jour depuis la version 1.1 vers la version 2.0, vous
devez d'abord mettre à jour vers la version 1.2 puis vers la version 2.0.
La seule étape optionnelle est l'intégration de vos personnalisations.

La version stable actuelle est la version 2.0.

.. Note::
   Si vous souhaitez améliorer Chimère prenez la branche *master* sur Git.

Les instructions sont données pour Debian Squeeze et Debian Wheezy.


Obtenir des nouvelles versions des dépendances
----------------------------------------------

Version 1.1 -> 1.2
******************

.. code-block:: bash

    apt-get install python-lxml libjs-jquery gpsbabel python-gdal

Version 1.2 -> 2.0
******************

Debian Squeeze
++++++++++++++
Activez les backports (http://backports-master.debian.org/Instructions/).
Puis installez les nouvelles dépendances ::

    apt-get install -t squeeze-backports python-django python-django-south \
                       python-simplejson libjs-jquery-ui python-pyexiv2 \
                       python-feedparser javascript-common libjs-jquery

Debian Wheezy
+++++++++++++

.. code-block:: bash

    apt-get install python-django-south python-simplejson libjs-jquery-ui \
                    python-pyexiv2 python-feedparser javascript-common

Si vous comptez réaliser des imports importants envisagez l'installation
de `Celery <http://celeryproject.org/>`_.

.. code-block:: bash

    apt-get install python-django-celery python-kombu

Obtenir les nouvelles sources
-----------------------------

Tout d'abord vous avez besoin de la nouvelle version du code source.
Pour la procédure d'installation, le code source doit être celui du dépôt Git.

Pour simplifier les instructions suivantes, quelques variables d'environnement
sont initialisées.

.. code-block:: bash

    CHIMERE_PATH=/srv/chimere
    CHIMERE_TAG=v1.2.0      # version 1.1 -> 1.2
    CHIMERE_TAG=v2.0-RC3    # version 1.2 -> 2.0
    CHIMERE_TAG=master      # version 2.0 -> master
    CHIMERE_LOCALNAME=mychimere

Le nom de votre projet (*CHIMERE_LOCALNAME*) est utilisé pour le nom de la
bibliothèque Python correspondant à votre projet ainsi que votre propre
branche Git.
En tant que bibliothèque Python, ce nom doit suivre les règles de nommage des
noms de variable Python : il doit comporter au moins une lettre et peut
comporter autant de nombres et de lettres que souhaité, le caractère tiret bas
(« _ ») est accepté. N'utilisez pas de caractères accentués. Ne commencez pas
par « _ » car cela a une signification particulière en Python.


Pour une précédente installation Git
************************************

.. code-block:: bash

    cd $CHIMERE_PATH
    git checkout -b $CHIMERE_LOCALNAME # seulement si vous n'avez pas encore
                                       # créé votre branche locale
    git stash # si vous avez des changements pas encore « commités »
    git checkout master
    git pull
    git checkout $CHIMERE_LOCALNAME
    git rebase $CHIMERE_TAG

Pour une précédente installation depuis une archive
***************************************************

Supprimez d'abord votre ancienne installation et obtenez la version Git :

.. code-block:: bash

    cd $CHIMERE_PATH
    cd ..
    rm -rf $CHIMERE_PATH
    git clone git://www.peacefrogs.net/git/chimere
    cd chimere
    git checkout $CHIMERE_TAG
    git checkout -b $CHIMERE_LOCALNAME


Mettre à jour les paramètres de base
************************************

Version 1.1 -> 1.2
++++++++++++++++++

.. code-block:: bash

    CHIMERE_APP_PATH=$CHIMERE_PATH/chimere
    vim $CHIMERE_APP_PATH/settings.py

Ajoutez les lignes suivantes (adaptez en fonction de vos installations
jquery et gpsbabel) :

.. code-block:: python

    JQUERY_URL = SERVER_URL + 'jquery/jquery-1.4.4.min.js'
    GPSBABEL = '/usr/bin/gpsbabel'
    # simplification des trajets avec une tolérance de 5 mètres
    GPSBABEL_OPTIONS = 'simplify,crosstrack,error=0.005k'

Version 1.2 -> 2.0
++++++++++++++++++

Patron de projet
................
Créez un nouveau patron de projet :

.. code-block:: bash

    cd $CHIMERE_PATH
    cp -ra $CHIMERE_PATH/example_project $CHIMERE_LOCALNAME
    CHIMERE_APP_PATH=$CHIMERE_PATH/$CHIMERE_LOCALNAME

local_settings
..............
Un fichier *local_settings* est maintenant utilisé.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    cp local_settings.py.sample local_settings.py
    vim local_settings.py

Reportez vos anciens paramètres de *settings.py* vers *local_settings.py*
(au minimum la configuration de votre base de données).
Le paramètre *ROOT_URLCONF* doit être mis à la valeur
« **nom_de_votre_projet.urls** ».

logs
....
Par défaut, des fichiers de *log* sont maintenant écrit dans le fichier :
« */var/log/django/chimere.log* ».

.. code-block:: bash

    mkdir /var/log/django
    touch /var/log/django/chimere.log
    chown www-data -R /var/log/django

Fichiers statiques
..................

Les fichiers statiques sont maintenant gérés avec
« **django.contrib.staticfiles** ».

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py collectstatic


Déplacez vos anciens fichiers statiques vers le nouveau répertoire :

.. code-block:: bash

    cp -ra $CHIMERE_PATH/chimere/static/* $CHIMERE_APP_PATH/static/
    cp -ra $CHIMERE_PATH/chimere/static/icons/* $CHIMERE_APP_PATH/media/icons/
    cp -ra $CHIMERE_PATH/chimere/static/upload $CHIMERE_APP_PATH/media/

Configuration du serveur Web
............................

Si vous utilisez Apache et WSGI pour mettre à disposition votre Chimère,
changez la configuration pour pointer vers le chemin correct de
configuration : « **nom_de_votre_projet.settings** ».

Changez la directive de votre serveur web pour qu'elle pointe vers le bon
répertoire statique de « **votre_chemin_vers_chimere/chimere/static** » en
« **votre_chemin_vers_chimere/nom_de_votre_projet/static** ».

Version 2.0 -> master
+++++++++++++++++++++

Mettez à jour les paramètres et les fichiers statiques.

.. code-block:: bash

    cp $CHIMERE_PATH/example_project/settings.py $CHIMERE_LOCALNAME
    ./manage.py collectstatic

Migration de la base de données
-------------------------------

Version 1.1 -> 1.2
******************

Les scripts de migration testent votre installation avant de faire des
changements. Vous n'aurez donc probablement pas de perte mais par précaution
avant de les lancer n'oubliez pas de faire une sauvegarde de votre base de
données.
Vous pouvez aussi faire une copie de votre base de données actuelle dans une
nouvelle base et faire la mise à jour sur cette nouvelle base de données.

La bibliothèque GDAL pour Python est nécessaire pour faire fonctionner ces
scripts (disponible avec le paquet *python-gdal* dans Debian).

Si vous souhaitez lancer le script de migration dans un environnement de
production, stoppez l'instance de Chimère avant d'exécuter le script de
migration.

Dans le fichier *settings.py* vérifiez que **chimere.scripts** fait partie
des *INSTALLED_APPS*.

Après cela, dans le répertoire d'installation de Chimère, exécutez simplement
le script.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    python ./scripts/upgrade.py

Version 1.2 -> 2.0
******************

Django South est maintenant utilisé pour les migrations de base de données.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py syncdb
    ./manage.py migrate chimere 0001 --fake # simule l'initialisation de la base
                                            # de données
    ./manage.py migrate chimere

Un champ descriptif est maintenant disponible pour les points d'intérêts. Si
vous souhaitez migrer un ancien *modèle de propriété* vers ce nouveau champ,
un script est disponible.

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ../chimere/scripts/migrate_properties.py
    # suivez les instructions

Version 2.0 -> master
*********************

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py syncdb
    ./manage.py migrate chimere

Mise à jour des traductions
---------------------------

Version 1.1 -> 1.2
******************

.. code-block:: bash

    cd $CHIMERE_APP_PATH
    ./manage.py compilemessages

Version 1.2 -> 2.0 -> master
****************************

.. code-block:: bash

    cd $CHIMERE_PATH/chimere
    django-admin compilemessages

Forcer le rafraîchissement du cache du navigateur des utilisateurs
------------------------------------------------------------------

Des changements importants au niveau des styles et du javascript sont faits
entre les différentes versions. Cela peut provoquer des dysfonctionnements
importants chez des utilisateurs dont le navigateur web a conservé les anciennes
versions de certains fichiers en cache. Il y a plusieurs moyens de forcer le
rafraîchissement de leur cache. Un de ceux-ci est de changer le chemin vers les
fichiers statiques. Pour faire cela, éditez votre fichier *local_settings.py* et
changez : ::

    STATIC_URL = '/static/'

en : ::

    STATIC_URL = '/static/v2.0.0/'

Changez la directive concernant les fichiers statiques sur le fichier de
configuration de votre serveur web.
Redémarrez alors le serveur web pour appliquer les changements.

