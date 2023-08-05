DjangoPyPI 2
============

DjangoPyPI is a Django application that provides a re-implementation of the 
`Python Package Index <http://pypi.python.org>`_.
Using Twitter Bootstrap for UI, forked from the original DjangoPyPi project,
DjangoPyPi2 provides an easy to use and manage interface.

Compatibility Note
------------------
This is a fork of the original ``djangopypi`` package. This version is somewhat
different than the original version by its design, and it might affect older
version in that the database table names are different than the original ones.
It is highly recommended that you install a fresh copy of this package and
manually transfer you data from your installation.

Since the table names in this installation are different, the same database can
be used for the migration.
Unfortunately there are too many versions of ``djangopypi`` our there, so it's
quite dangerous to create ``south`` migrations for them.
Sorry for the inconvenience.

Installation
------------

Path
____

The first step is to get ``djangopypi2`` into your Python path.

Buildout
++++++++

Simply add ``djangopypi2`` to your list of ``eggs`` and run buildout again it 
should downloaded and installed properly.

EasyInstall/Setuptools
++++++++++++++++++++++

If you have setuptools installed, you can use ``easy_install djangopypi2``

Manual
++++++

Download and unpack the source then run::

    $ python setup.py install

Django Settings
_______________

Make sure all the following apps are in your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'djangopypi2.apps.pypi_ui',
        'djangopypi2.apps.pypi_config',
        'djangopypi2.apps.pypi_frontend',
    )

And add the following to ``TEMPLATE_CONTEXT_PROCESSORS`` (this setting
is absent by default, in which case simply add it)::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'django.contrib.auth.context_processors.auth',
        'django.core.context_processors.request',
    )

Then, make sure the ``STATIC_ROOT`` setting is configured properly::

    STATIC_ROOT = '/path/to/static/root'

And update the urlpatterns to include ``djangopypi2.urls``::

    urlpatterns = patterns("",
        ...
        url(r'', include("djangopypi2.urls"))
    )

This serves the following:
* ``/``:: Normal web interface.
* ``/pypi/``:: Repository interface.
* ``/simple/``:: Simple interface.
* ``/static/``:: Your static files (only if DEBUG=True)
* ``/favicon.ico``

Finally, run the following Django commands to sync everything ``syncdb``::

    $ ./manage.py syncdb
    $ ./manage.py migrate pypi_config
    $ ./manage.py migrate pypi_frontend
    $ ./manage.py loaddata initial
    $ ./manage.py collectstatic

Package upload directory
++++++++++++++++++++++++

By default packages are uploaded to ``<MEDIA_ROOT>/dists`` so you need both
to ensure that ``MEDIA_ROOT`` is assigned a value and that the
``<MEDIA_ROOT>/dists`` directory is created and writable by the web server.

You may change the directory to which packages are uploaded by setting
``DJANGOPYPI_RELEASE_UPLOAD_TO``; this will be a sub-directory of ``MEDIA_ROOT``.


Package download handler
++++++++++++++++++++++++

Packages are downloaded from the following URL:
``<host>/simple/<package>/dists/<package>-<version>.tar.gz#<md5 hash>``

You will need to configure either your development server to deliver the
package from the upload directory, or your web server (e.g. NGINX or Apache).

To configure your Django development server ensure that ``urls.py`` looks
something like following::

 import os
 from django.conf.urls import patterns, include, url
 from django.conf import settings

 # ... other code here including Django admin auto-discover ...

 urlpatterns = patterns('',
     # ... url patterns...

     url(r'^simple/[\w\d_\.\-]+/dists/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': os.path.join(settings.MEDIA_ROOT,
                                            settings.DJANGOPYPI_RELEASE_UPLOAD_TO)}),
     url(r'', include("djangopypi2.urls")),

     # .. url patterns...
 )

This should only be used for the Django development server.

When using a web server, configure that to deliver packages from the
upload dist directory directly from this URL. For example, you may have
a clause in an NGINX configuration file something like the following::

 server {
   ... configuration...
   
   location ~ ^/simple/[a-zA-Z0-9\,\-\.]+/dists/ {
       alias /path/to/upload/dists/;
   }

   ... configuration...
 }

Uploading to your PyPI
----------------------

Assuming you are running your Django site locally for now, add the following to 
your ``~/.pypirc`` file::

    [distutils]
    index-servers =
        pypi
        local

    [pypi]
    username:user
    password:secret

    [local]
    username:user
    password:secret
    repository:http://localhost:8000/pypi/

Uploading a package: Python >=2.6
_________________________________

To push the package to the local pypi::

    $ python setup.py register -r local sdist upload -r local


Uploading a package: Python <2.6
________________________________

If you don't have Python 2.6 please run the command below to install the 
backport of the extension for multiple repositories::

     $ easy_install -U collective.dist

Instead of using register and dist command, you can use ``mregister`` and 
``mupload`` which are a backport of python 2.6 register and upload commands 
that supports multiple servers.

To push the package to the local pypi::

    $ python setup.py mregister -r local sdist mupload -r local

Installing a package with pip
-----------------------------

To install your package with pip::

 $ pip install -i http://my.pypiserver.com/simple/ <PACKAGE>

If you want to fall back to PyPi or another repository in the event the
package is not on your new server, or in particular if you are installing a number
of packages, some on your private server and some on another, you can use
pip in the following manner::

 $ pip install -i http://localhost:8000/simple/ \
   --extra-index-url=http://pypi.python.org/simple/ \
   -r requirements.txt

(substitute your djangopypi2 server URL for the ``localhost`` one in this example)

The downside is that each install of a package hosted on the repository in
``--extra-index-url`` will start with a call to the first repository which
will fail before pip falls back to the alternative.

Copyright and Credits
---------------------
Originally written by Benjamin Liles from http://github.com/benliles/djangopypi

This software uses Twitter Bootstrap for UI: http://twitter.github.com/bootstrap/

Favicon taken from http://pypi.python.org/favicon.ico
