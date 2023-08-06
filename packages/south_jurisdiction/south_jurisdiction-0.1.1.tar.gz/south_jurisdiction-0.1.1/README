south-jurisdiction
==================

Motivation
----------
South isn't great at handling differing requirements from multiple databases
in a django application.

South assumes that there will at least be a south_migration_history table
available at the point of running migrate against a given database.

This is fine when your django app is only dealing with one default database,
but becomes much less pleasant when wanting to add extra database sources that
perhaps south shouldn't have jurisdiction over.


Let's say your ``django.conf`` settings look something like::

    DATABASES = {
        'default': {
            ...
            'NAME': 'my_own_db',
            ...
        },

        'super_secure': {
            ...
            'NAME': 'super_secure',
            ...
        }
    }

You wouldn't want ``syncdb`` to create tables in the ``super_secure`` DB, and
that would be achieved by creating a database router, along with an
``allow_syncdb`` method and include that in a ``DATABASE_ROUTER`` setting.
Done.

You **also** wouldn't want ``migrate`` to do anything in super_secure. As it
stands, ``south`` fails at this because the first thing it does is see if there
are any migrations in the database by looking at the south_migration_history
table. Because syncdb didn't create this you get FAILURE.

Solution
--------

South jurisdiction introduces a new setting to the django settings module::

    SOUTH_MANAGED_DBS = []

This is intended to be populated with the keys of the databases that you want
south to manage. In the above example it would read::

    SOUTH_MANAGED_DBS = ['default']

Any attempt to migrate on a database not included in SOUTH_MANAGED_DBS is
rejected gracefully.

Configuration
-------------

 - Add ``"south_jurisdiction"`` to ``INSTALLED_APPS`` in your settings, after
   the ``"south"`` app.
 - Use the new ``SOUTH_MANAGED_DBS`` setting available to you.
 - If you don't want to run the south_jurisdiction tests, use the
   ``SKIP_SOUTH_TESTS`` setting in the same way as you do for south.

