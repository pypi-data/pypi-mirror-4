from django.conf import settings

try:
    from south.management.commands import migrate
except ImportError:
    print "You need to install south for south_jurisdiction to work."
    import sys
    sys.exit()


class Command(migrate.Command):

    def handle(self, *args, **kwargs):
        db = kwargs['database']
        if db in settings.SOUTH_MANAGED_DBS:
            print ("Managed db '{0}' is getting migrated...".format(db))
            super(Command, self).handle(*args, **kwargs)
        else:
            print ("Db '{0}' is not managed by ``south_jurisdiction``."
                   " Skipping.".format(db))
