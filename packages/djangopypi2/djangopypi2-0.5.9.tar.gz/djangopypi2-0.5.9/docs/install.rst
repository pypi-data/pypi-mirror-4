Installation & Configuration
============================

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
    $ pip install gunicorn djangopypi2

    # Configure our installation
    $ manage-pypi-site syncdb
    $ manage-pypi-site collectstatic
    $ manage-pypi-site loaddata initial

That's it, we're now ready to run our server

Where data is kept
------------------
By default ``djangopypi2`` installs and runs from ``~/.djangopypi2``, meaning
the ``.djangopypi2`` directory inside the homedir of the user running the web
server.

This can be overridden by setting the ``DJANGOPYPI2_ROOT`` environment variable.

For example, to install with a specific ``PROJECT_ROOT`` /etc/djangopypi2::
    
    # Configure our installation
    $ DJANGOPYPI2_ROOT=/etc/djangopypi2 manage-pypi-site syncdb
    $ DJANGOPYPI2_ROOT=/etc/djangopypi2 manage-pypi-site collectstatic
    $ DJANGOPYPI2_ROOT=/etc/djangopypi2 manage-pypi-site loaddata initial

Running
-------
It's easiest to see our server running by executing::

    $ gunicorn_django djangopypi2.website.settings

Then surfing to http://localhost:8000/ .

For a permanent setup, simply create a ``supervisor <http://supervisord.org/>``
configuration (you can omit the ``environment`` setting if you didn't specify a
different project root)::

    [program:djangopypi2]
    user = www-data
    directory = /path/to/virtualenv
    command = /path/to/virtualenv/bin/gunicorn_django djangopypi2.website.settings
    environment = DJANGOPYPI2_ROOT='/path/to/djangopypi2'

Configuration
-------------
When first running ``djangopypi2``, a file called ``settings.json`` will be created
in the ``PROJECT_ROOT`` directory::

    {
        "DEBUG": true,
        "ADMINS": [],
        "LANGUAGE_CODE": "en-us",
        "TIME_ZONE": "America/Chicago",
        "WEB_ROOT": "/",
        "ALLOW_VERSION_OVERWRITE: ""
    }

The ``DEBUG``, ``ADMINS``, ``LANGUAGE_CODE`` and ``TIME_ZONE`` are exactly the same
as in any Django ``settings.py`` file.

The ``WEB_ROOT`` setting allows for reverse proxy support. By specifying any other
root than ``/`` you can move the entire site to be served on a different web root.

The ``ALLOW_VERSION_OVERWRITE`` setting allows you to selectively allow clients to
overwrite package distributions based on the version number. This is a regular 
expression, with the default empty string meaning 'deny all'. A common use-case
example of this is to allow development versions to be overwritten, but not released
versions::

    "ALLOW_VERSION_OVERWRITE": "\\.dev.*$"

This will match ``1.0.0.dev``, ``1.0.0.dev3``, but not ``1.0.0``. Note the escaping
of the backslash character - this is required to conform to the json format. 


Package upload directory
-------------------------
Packages are uploaded to ``PROJECT_ROOT/media/dists/`` by default.

You can change this setting by setting up a Django project with more specific
settings, or have a look at the admin interface's ``Global Configuration``
section to see if you configure your desired behavior in there.
