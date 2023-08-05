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

DjangoPyPi2 is a self-contained Django project along with its apps. If you want
fine-grained control, you can looks at the sources of the apps found in the
``djangopypi2.apps`` package.

The most simple way to install ``djangopypi2`` is by::

    # Make sure we run with Bash, create a virtualenv and install packages
    $ bash
    $ virtualenv pypi-site
    $ source pypi-site/bin/activate
    $ pip install django gunicorn djangopypi2

    # Configure our installation (all data is kept in ~/.djangopypi2)
    $ manage-pypi-site syncdb
    $ manage-pypi-site collectstatic
    $ manage-pypi-site loaddata initial

That's it, we're now ready to run our server

Running
-------
It's easiest to see our server running by executing::

    $ gunicorn_django djangopypi2.website.settings

Then surfing to http://localhost:8000/ .

For a permanent setup, simply create a ``supervisor <http://supervisord.org/>``
configuration::

    [program:djangopypi2]
    user = www-data
    directory = /path/to/virtualenv
    command = /path/to/virtualenv/bin/gunicorn_django djangopypi2.website.settings

Configuration
-------------
All the data and settings of ``djangopypi2`` resides by default in a the directory
``~/.djangopypi2``, meaning ``.djangopypi2`` inside the homedir of the user running
the web server.

You can create a file named ``settings.py`` in that directory to override any
available Django settings, and basically you'd want to create a file like this::

    # ~/.djangopypi2/settings.py

    DEBUG = False                 # Control DEBUG on/off
    TIME_ZONE = 'Your/Time/Zone'  # Just like in any Django settings.py file
    ADMINS = (
        ('Your name', 'your@email'),
    )

Package upload directory
-------------------------
Packages are uploaded to ``~/.djangopypi2/media/dists/`` by default.

You can change this setting by setting up a Django project with more specific
settings, or have a look at the admin interface's ``Global Configuration``
section to see if you configure your desired behavior in there.

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
