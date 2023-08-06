from django.conf import settings

try:
    from south.management.commands import migrate
except ImportError:
    print "You need to install south for south_jurisdiction to work."
    import sys
    sys.exit()

ALL = 'Migrate all the things!'


class Command(migrate.Command):

    def handle(self, *args, **kwargs):
        """Call migrate if the db is a SOUTH_MANAGED_DBS.

        If SOUTH_MANAGED_DBS has not beeen set in django.conf.settings, then
        the call to migrate goes ahead.
        """
        db = kwargs['database']
        south_managed_dbs = getattr(settings, 'SOUTH_MANAGED_DBS', ALL)
        if db in south_managed_dbs or south_managed_dbs == ALL:
            print ("Managed db '{0}' is getting migrated...".format(db))
            super(Command, self).handle(*args, **kwargs)
        else:
            print ("Db '{0}' is not managed by ``south_jurisdiction``."
                   " Skipping.".format(db))
