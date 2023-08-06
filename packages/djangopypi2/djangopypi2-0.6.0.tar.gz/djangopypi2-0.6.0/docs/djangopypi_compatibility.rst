Compatibility with original DjangoPyPi
======================================
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

Migrating from DjangoPyPi
-------------------------
If you do want to migrate from DjangoPyPi, the best method is to install a fresh
copy of DjangoPyPi2 and import all packages from it.
