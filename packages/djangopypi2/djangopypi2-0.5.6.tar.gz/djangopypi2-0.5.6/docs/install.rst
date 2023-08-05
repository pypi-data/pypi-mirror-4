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

After first running ``djangopypi2``, a file called ``settings.json`` will be created
in the ``~/.djangopypi2`` directory::

    {
        "DEBUG": true,
        "ADMINS": [],
        "LANGUAGE_CODE": "en-us",
        "TIME_ZONE": "America/Chicago",
        "WEB_ROOT": "/"
    }

The ``DEBUG``, ``ADMINS``, ``LANGUAGE_CODE`` and ``TIME_ZONE`` are exactly the same
as in any Django ``settings.py`` file.

The ``WEB_ROOT`` setting allows for reverse proxy support. By specifying any other
root than ``/`` you can move the entire site to be served on a different web root.

Package upload directory
-------------------------
Packages are uploaded to ``~/.djangopypi2/media/dists/`` by default.

You can change this setting by setting up a Django project with more specific
settings, or have a look at the admin interface's ``Global Configuration``
section to see if you configure your desired behavior in there.
