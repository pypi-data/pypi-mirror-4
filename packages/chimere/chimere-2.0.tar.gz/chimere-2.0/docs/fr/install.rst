.. -*- coding: utf-8 -*-

============
Installation
============

:Auteur: Étienne Loks
:date: 2012-11-28
:Copyright: CC-BY 3.0

Ce document présente l'installation de Chimère.
Il a été mis à jour pour la version 2.0.0 de Chimère.

Pré-requis
**********

 - `Apache <http://www.apache.org/>`_ version 2.x
 - `Python <http://www.python.org/>`_ versions 2.6 ou 2.7
 - `Django <http://www.djangoproject.com/>`_ >= version 1.4
 - `South <http://south.aeracode.org/>`_
 - `Postgres <http://www.postgresql.org/>`_ >= version 8.x
 - `Gettext <http://www.gnu.org/software/gettext/>`_
 - `Psycopg2 <http://freshmeat.net/projects/psycopg/>`_
 - `Python Imaging Library <http://www.pythonware.com/products/pil/>`_
 - `Pyexiv2 <http://tilloy.net/dev/pyexiv2/>`_
 - `Beautiful Soup <http://www.crummy.com/software/BeautifulSoup/>`_
 - python-simplejson
 - python-gdal
 - `Lxml <http://lxml.de/>`_
 - `Jquery <http://jquery.com/>`_ version 1.7.1 or better
 - `Jquery-ui <http://jqueryui.com/>`_
 - `Universal Feed Parser <https://code.google.com/p/feedparser/>`_

geodjango fait partie de Django depuis la version 1.0 mais nécessite quelques
dépendances supplémentaires :

 - `geos <http://trac.osgeo.org/geos/>`_ 3.0.x
 - `proj.4 <http://trac.osgeo.org/proj/>`_ 4.4 to 4.6
 - `posgis <http://postgis.refractions.net/>`_ versions 1.2.1 ou 1.3.x
 - `gdal <http://www.gdal.org/>`_


Optionnel (mais recommandé) :

 - `tinymce <http://tinymce.moxiecode.com/>`_
 - `gpsbabel <http://www.gpsbabel.org/>`_
 - django-celery pour une meilleure gestion des imports importants

La manière la plus simple de satisfaire à ces pré-prequis est de les installer
par le biais des dépôts de votre distribution Linux préférée. Par exemple
pour Debian Wheezy : ::

    apt-get install apache2 python python-django python-django-south \
        postgresql-9.1 gettext python-psycopg2 python-imaging \
        python-pyexiv2 python-beautifulsoup python-simplejson python-gdal \
        python-lxml libjs-jquery libjs-jquery-ui python-feedparser \
        libgeos-3.3.3 proj-bin postgresql-9.1-postgis gdal-bin \
        tinymce gpsbabel python-django-celery javascript-common 

Pour Debian Squeeze (il est nécessaire d'activer les backports) : ::

    apt-get install -t squeeze-backports python-django libjs-jquery

    apt-get install apache2 python python-django python-django-south \
        postgresql-8.4 gettext python-psycopg2 python-imaging \
        python-pyexiv2 python-beautifulsoup python-simplejson python-gdal \
        python-lxml libjs-jquery libjs-jquery-ui python-feedparser \
        libgeos-3.2.0 proj-bin postgresql-8.4-postgis gdal-bin \
        tinymce gpsbabel javascript-common 

Le paquet *python-django-celery* n'existe pas pour Debian Squeeze.

Si ces paquets n'ont pas d'équivalents dans les dépôts de votre distribution
Linux, référez-vous aux sites web de ces applications.

Configuration de la base de données
***********************************

Maintenant que postgres et postgis sont installés, vous avez besoin de créer
un nouvel utilisateur pour Chimère : ::

    su postgres
    createuser --echo --adduser --createdb --encrypted --pwprompt chimere-user

Ensuite, vous avez besoin de créer la base de données et d'initialiser les types
géographiques (adaptez les chemins par rapport à vos besoins) : ::

    PG_VERSION=9.1 # 8.4 pour debian Squeeze
    createdb --echo --owner chimere-user --encoding UNICODE chimere "Ma base de données Chimère"
    createlang plpgsql chimere # seulement nécessaire sous Debian Squeeze
    psql -d chimere -f /usr/share/postgresql/$PG_VERSION/contrib/postgis-1.5/postgis.sql
    psql -d chimere -f /usr/share/postgresql/$PG_VERSION/contrib/postgis-1.5/spatial_ref_sys.sql

Installer les sources
*********************

Choisissez un chemin où installer Chimère ::

    INSTALL_PATH=/var/local/django
    mkdir $INSTALL_PATH

Depuis une archive
++++++++++++++++++

La dernière version « stable » est disponible dans ce `répertoire 
<http://www.peacefrogs.net/download/chimere/>`_.
Prenez garde à prendre la dernière version de la branche souhaitée
(par exemple la dernière version de la branche 1.0 est la version 1.0.2). ::

    wget http://www.peacefrogs.net/download/chimere -q -O -| html2text
    (...)
    [[   ]] chimere-1.0.0.tar.bz2     17-Nov-2010 16:51  53K
    [[   ]] chimere-1.0.1.tar.bz2     17-Nov-2010 16:51  53K
    [[   ]] chimere-1.0.2.tar.bz2     17-Nov-2010 16:51  53K
    (...)

    wget http://www.peacefrogs.net/download/chimere/chimere-1.0.2.tar.bz2

Téléchargez, décompressez et déplacez les fichiers dans un répertoire lisible
par l'utilisateur de votre serveur web (www-data pour Debian). ::

    cd $INSTALL_PATH
    tar xvjf chimere-last.tar.bz2
    chown -R myusername:www-data chimere

Depuis le dépôt Git
+++++++++++++++++++

Une autre solution est d'obtenir les sources depuis le dépôt Git : ::

    cd $INSTALL_PATH
    git clone git://www.peacefrogs.net/git/chimere
    cd chimere
    git tag -l # lister les versions
    git checkout v2.0 # choisir la version désirée


Créez un patron pour votre projet
*********************************

Il y a un exemple de projet fourni (*example_project*). Copiez-le et 
modifiez-le (ou utilisez un autre projet basé sur Chimère) : ::

    cd $INSTALL_PATH/chimere
    cp -ra example_project mychimere_project

Le nom de votre projet est utilisé pour le nom de la bibliothèque Python
correspondant à votre projet.
En tant que bibliothèque Python, ce nom doit suivre les règles de nommage des
noms de variable Python : il doit comporter au moins une lettre et peut
comporter autant de nombres et de lettres que souhaité, le caractère tiret bas 
(« _ ») est accepté. N'utilisez pas de caractères accentués. Ne commencez pas 
par « _ » car cela a une signification particulière en Python.

Dans le répertoire de votre application Chimère créez un fichier
*local_settings.py* qui correspond à votre configuration.
Un fichier de base est fourni (*local_settings.py.example*) et des descriptions
courtes des variables les plus pertinentes sont données sous celui-ci
(survolez-les au minimum). La plupart de ces paramétrages sont initialisés dans
le fichier *settings.py*. ::

    cd $INSTALL_PATH/chimere/mychimere_project
    cp local_settings.py.sample local_settings.py
    vim local_settings.py

:Champs:

    * DATABASES : paramètres relatifs à la base de données
    * PROJECT_NAME : nom du projet
    * SECRET_KEY : une clé secrète pour l'installation de votre application
      Django. Cette clé est utilisée pour les signatures cryptographiques de
      l'application et doit être initialisée à une valeur unique et non
      devinable. **Modifiez-là !**
    * ROOT_URLCONF : module Python de configuration des urls pour votre projet.
      Cela devrait être quelque chose comme : 'mychimere_project.urls'
    * EMAIL_HOST : SMTP du serveur de courriel pour envoyer des courriels
    * TINYMCE_URL : url du chemin vers tinymce (le chemin par défaut est adapté
      pour une installation sous Debian avec le paquet tinymce installé)
    * JQUERY_JS_URLS : liste des adresses des fichiers javascript jquery et
      jquery-ui (les valeurs par défaut sont appropriées pour une installation
      sous Debian avec les paquets libjs-jquery et libjs-jquery-ui installés)
    * JQUERY_CSS_URLS : liste des adresses des fichiers CSS jquery et
      jquery-ui (les valeurs par défaut sont appropriées pour une installation
      sous Debian avec les paquets libjs-jquery et libjs-jquery-ui installés)
    * GPSBABEL : chemin de gpsbabel (la valeur par défaut est appropriée pour 
      une installation sous Debian avec le paquet gpsbabel installé)
    * TIME_ZONE : fuseau horaire local de cette installation
    * LANGUAGE_CODE : code de langage pour cette installation

Gérez les permissions du dossier de média : ::

    cd $INSTALL_PATH/chimere/mychimere_project
    chown -R user:www-data media
    chmod -R g+w media

Créez le fichier de log : ::

    mkdir /var/log/django
    touch /var/log/django/chimere.log
    chown -R root:www-data /var/log/django/
    chmod -R g+w /var/log/django/

Regroupez les fichiers static dans un seul répertoire : ::

    cd $INSTALL_PATH/chimere/mychimere_project
    ./manage.py collectstatic

Compilation des langages
************************

Si votre langage est disponible dans le dossier *chimere/locale/*, il est juste
nécessaire de le compiler.
Pour faire cela, il faut lancer la commande suivante (ici, **fr** est pour le
français, remplacez cela avec le code de langage approprié) : ::

    cd $INSTALL_PATH/chimere/chimere/
    django-admin compilemessages -l fr

Si votre langage n'est pas disponible, n'hésitez pas à créer le fichier **po**
par défaut et à le proposer (les contributions sont bienvenues).
La procédure est explicité ci-dessous.

Il est d'abord nécessaire de créer le fichier po par défaut (bien sûr remplacez
**fr** par le code du langage que vous souhaitez créer) : ::

    django-admin makemessages -l fr

Il doit y avoir maintenant un fichier *django.po* dans le répertoire
*locale/fr/LC_MESSAGES*. Ensuite il faut le compléter avec votre
traduction.

Une fois le votre fichier de traduction complété, il suffit de le
compiler de la même manière que vous l'auriez fait si ce fichier était
initialement disponible.

Initialisation de la base de données
************************************

Créez les tables de la base de données (toujours dans le répertoire de votre
projet) : ::

    cd $INSTALL_PATH/chimere/mychimere_project
    ./manage.py syncdb


Vous aurez à rentrer les informations pour la création du compte administrateur
(les pages d'administration se trouvent à l'adresse : 
http://where_is_chimere/admin/). Ensuite pour créer les tables de la base de
données gérées par Django-South : ::

    ./manage.py migrate

La base de données est en place, félicitations !

Si vous voulez remplir votre installation avec des données par défaut (ne le
faites pas sur une instance de Chimère contenant déjà des données !) : ::

    ./manage.py loaddata ../chimere/fixtures/default_data.json

Configuration du serveur web
****************************

Configuration d'Apache avec mod_wsgi
++++++++++++++++++++++++++++++++++++

Installez *mod_wsgi* pour Apache : ::

    apt-get install libapache2-mod-wsgi


Créez et éditez la configuration de Chimère en fonction de votre installation ::

    cp $INSTALL_PATH/chimere/apache/django.wsgi \
            $INSTALL_PATH/chimere/apache/mydjango.wsgi
    vim $INSTALL_PATH/chimere/apache/mydjango.wsgi
    cp $INSTALL_PATH/chimere/apache/apache-wsgi.conf \
            /etc/apache2/sites-available/chimere
    vim /etc/apache2/sites-available/chimere
    # créer le répertoire des logs
    mkdir /var/log/apache2/chimere/
    chown www-data /var/log/apache2/chimere/

Adaptez les fichiers *mydjango.wsgi* (avec le chemin correct *sys* des
bibliothèques Python de Chimère et le nom correct pour le module) et le fichier
*chimere* de Apache (avec le nom de serveur correct et les chemins corrects).

Pour activer le site web, rechargez Apache : ::

    a2ensite chimere
    /etc/init.d/apache2 reload

Si vous avez des problèmes de dépôt de fichier avec des caractères Unicode dans
leurs noms, activez la locale appropriée dans Apache. Sur un serveur Debian avec
UTF-8 comme codage par défaut, dans le fichier */etc/apache2/envvars*
décommentez la ligne suivante : ::

    . /etc/default/locale


