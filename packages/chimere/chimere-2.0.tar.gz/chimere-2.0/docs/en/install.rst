.. -*- coding: utf-8 -*-

============
Installation
============

:Author: Étienne Loks
:date: 2012-11-28
:Copyright: CC-BY 3.0

This document presents the installation of Chimère.
It has been updated for version 2.0.0.

Prerequisites
*************

 - `Apache <http://www.apache.org/>`_ version 2.x
 - `Python <http://www.python.org/>`_ versions 2.6 or 2.7
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

geodjango is a part of django since version 1.0 but it has some specific
(geographically related) additional dependencies:

 - `geos <http://trac.osgeo.org/geos/>`_ 3.0.x
 - `proj.4 <http://trac.osgeo.org/proj/>`_ 4.4 to 4.6
 - `postgis <http://postgis.refractions.net/>`_ versions 1.2.1 or 1.3.x
 - `gdal <http://www.gdal.org/>`_


Optionaly (but recommanded):

 - `tinymce <http://tinymce.moxiecode.com/>`_
 - `gpsbabel <http://www.gpsbabel.org/>`_
 - django-celery if you want to manage large imports


The simpliest way to obtain these packages is to get them from your favorite
Linux distribution repositories. For instance on Debian Wheezy::

    apt-get install apache2 python python-django python-django-south \
        postgresql-9.1 gettext python-psycopg2 python-imaging \
        python-pyexiv2 python-beautifulsoup python-simplejson python-gdal \
        python-lxml libjs-jquery libjs-jquery-ui python-feedparser \
        libgeos-3.3.3 proj-bin postgresql-9.1-postgis gdal-bin \
        tinymce gpsbabel python-django-celery javascript-common 


On Debian Squeeze (you need to activate backports)::

    apt-get install -t squeeze-backports python-django libjs-jquery

    apt-get install apache2 python python-django python-django-south \
        postgresql-8.4 gettext python-psycopg2 python-imaging \
        python-pyexiv2 python-beautifulsoup python-simplejson python-gdal \
        python-lxml libjs-jquery libjs-jquery-ui python-feedparser \
        libgeos-3.2.0 proj-bin postgresql-8.4-postgis gdal-bin \
        tinymce gpsbabel javascript-common 

The package *python-django-celery* doesn't exist for Debian Squeeze.

If these packages do not exist in your distribution's repository, please refer
to the applications' websites.

Database configuration
**********************

Now that postgres and postgis are installed, you need to create a new user for
Chimère::

    su postgres
    createuser --echo --adduser --createdb --encrypted --pwprompt chimere-user

Then, you have to create the database and initialize the geographic types (adapt
the paths accordingly to your needs)::

    PG_VERSION=9.1 # 8.4 for debian Squeeze
    createdb --echo --owner chimere-user --encoding UNICODE chimere "My Chimère database"
    createlang plpgsql chimere # only necessary on Debian Squeeze
    psql -d chimere -f /usr/share/postgresql/$PG_VERSION/contrib/postgis-1.5/postgis.sql
    psql -d chimere -f /usr/share/postgresql/$PG_VERSION/contrib/postgis-1.5/spatial_ref_sys.sql

Installing the sources
**********************

.. Note::
   If you are considering to contribute on Chimère get the Git master.

Choose a path to install your Chimère::

    INSTALL_PATH=/var/local/django
    mkdir $INSTALL_PATH

From an archive
+++++++++++++++

The last "stable" version is available in this `directory <http://www.peacefrogs.net/download/chimere/>`_.
Take care of getting the last version in the desired X.Y branch (for instance
the last version for the 1.0 branch is version 1.0.2).::

    wget http://www.peacefrogs.net/download/chimere -q -O -| html2text
    (...)
    [[   ]] chimere-1.0.0.tar.bz2     17-Nov-2010 16:51  53K
    [[   ]] chimere-1.0.1.tar.bz2     17-Nov-2010 16:51  53K
    [[   ]] chimere-1.0.2.tar.bz2     17-Nov-2010 16:51  53K
    (...)

    wget http://www.peacefrogs.net/download/chimere/chimere-1.0.2.tar.bz2

Download, unpack and move the files in an apache user (www-data for Debian)
readable directory::

    cd $INSTALL_PATH
    tar xvjf chimere-last.tar.bz2
    chown -R myusername:www-data chimere

From the Git repository
+++++++++++++++++++++++

Another solution is to get it from the Git repository::

    cd $INSTALL_PATH
    git clone git://www.peacefrogs.net/git/chimere
    cd chimere
    git tag -l # list tagged versions
    git checkout v2.0 # checkout the desired version


Creating a custom project template
**********************************

There, a default project is provided (*example_project*). Copy and modify 
it (or get another project based on Chimère)::

    cd $INSTALL_PATH/chimere
    cp -ra example_project mychimere_project

Your project name is used for the name of the Python package of your template.
As a Python package it should follow the rule of Python variable name:
it must contain at least one letter and can have a string of numbers, letters and
underscores ("_") to any length. Don't use accentuated letters. Don't begin the
name by "_" because it has special significance in Python.

In your Chimère application directory create *local_settings.py* to fit to your
configuration.
A base template is provided (*local_settings.py.example*) and short descriptions
of the more relevant fields are given below (at least check them). Most of
these settings are initialized in *settings.py*. ::

    cd $INSTALL_PATH/chimere/mychimere_project
    cp local_settings.py.sample local_settings.py
    vim local_settings.py

:Fields:

    * DATABASES: parameters for the database
    * PROJECT_NAME: name of the project
    * SECRET_KEY: a secret key for a particular Django installation. This is
      used to provide cryptographic signing, and should be set to a unique,
      unpredictable value. **Change it!**
    * ROOT_URLCONF: url configuration for your project something like:
      'mychimere_project.urls'
    * EMAIL_HOST: smtp of an email server to send emails
    * TINYMCE_URL: url to tinymce path (default is appropriate for a Debian
      installation with tinymce package installed)
    * JQUERY_JS_URLS: list of jquery and jquery-ui javascript urls (default is
      appropriate for a Debian installation with libjs-jquery libjs-jquery-ui
      packages installed)
    * JQUERY_CSS_URLS: list of jquery and jquery-ui CSS urls (default is
      appropriate for a Debian installation with libjs-jquery libjs-jquery-ui
      packages installed)
    * GPSBABEL: path to gpsbabel  (default is appropriate for a Debian
      installation with gpsbabel package installed)
    * TIME_ZONE: local time zone for this installation
    * LANGUAGE_CODE: language code for this installation

Manage media path permission::

    cd $INSTALL_PATH/chimere/mychimere_project
    chown -R user:www-data media
    chmod -R g+w media

Create log file::

    mkdir /var/log/django
    touch /var/log/django/chimere.log
    chown -R root:www-data /var/log/django/
    chmod -R g+w /var/log/django/

Regroup static files in one path::

    cd $INSTALL_PATH/chimere/mychimere_project
    ./manage.py collectstatic

Compiling languages
*******************

If your language is available in the directory *chimere/locale/*, you will just
need to get it compiled. This can be done with the following command (here,
**fr** stands for French, replace it with the appropriate language code)::

    cd $INSTALL_PATH/chimere/chimere/
    django-admin compilemessages -l fr

If your language is not available, feel free to create the default po file and
to submit it, contributions are well appreciated. Procedure is as follows:

You first need to create the default po file (of course, replace **fr**
according to the language you choose to create)::

    django-admin makemessages -l fr

There should now be a *django.po* file in *locale/fr/LC_MESSAGES*. Complete it
with your translation.

Now that the translation file is completed, just compile it the same way you
would have if the language file was already available.

Database initialisation
***********************

Create the appropriate tables (still being in your Chimère project directory)::

    cd $INSTALL_PATH/chimere/mychimere_project
    ./manage.py syncdb

You will be prompted for the creation of an administrator account
(administration can be found at: http://where_is_chimere/admin/). Then you have
to create tables managed with Django-South::

    ./manage.py migrate

The database is set, congratulations!

If you want to populate your installation with default data (don't do this on
an already populated instance!)::

    ./manage.py loaddata ../chimere/fixtures/default_data.json

Webserver configuration
***********************

Apache configuration with mod_wsgi
++++++++++++++++++++++++++++++++++

Install *mod_wsgi* for Apache::

    apt-get install libapache2-mod-wsgi


Create and edit a configuration for Chimère::

    cp $INSTALL_PATH/chimere/apache/django.wsgi \
                   $INSTALL_PATH/chimere/apache/mydjango.wsgi
    vim $INSTALL_PATH/chimere/apache/mydjango.wsgi
    cp $INSTALL_PATH/chimere/apache/apache-wsgi.conf \
                   /etc/apache2/sites-available/chimere
    vim /etc/apache2/sites-available/chimere
    # create log dir
    mkdir /var/log/apache2/chimere/
    chown www-data /var/log/apache2/chimere/

Adapt the files *mydjango.wsgi* (with the correct sys path and the correct
module) and Apache *chimere* (with the correct servername and correct paths).

To activate the website, reload apache::

    a2ensite chimere
    /etc/init.d/apache2 reload

If you encounter problem with the upload of files with Unicode chars in their
names, activate the appropriate locale in Apache. On a Debian server with UTF-8
as default encoding, in the file */etc/apache2/envvars* uncomment the following
line::

    . /etc/default/locale


