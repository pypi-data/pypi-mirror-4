import sys
from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand

from migrator.models import MigratedObject


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
            make_option('-a', '--all', default=None, action="store_true", dest='all',
                    help='Delete every migrated object'),
            make_option('-m', '--is-migrating', default=None, dest='is_migrating',
                    help='Delete the migrated object that are migrating'),
            make_option('-c', '--is-created', default=None, dest='is_created',
                    help='Delete the migrated object that are created'),
            make_option('-e', '--has-errors', default=None, dest='has_errors',
                    help='Delete the migrated object that have errors'),
            make_option('-d', '--migration-date', default=None, dest='migration_date',
                    help='Delete the migrated object that was created before this date'),
            make_option('-i', '--content-type-id', default=None, dest='content_type_id',
                    help='Delete the migrated object that have this content type'),
    )

    usage_str = "Usage: ./manage.py delete_migrated_objects [-a|-m (0, 1)|-c (0, 1)|-e (0, 1)|-d yy/mm/dd|-i PK]"

    def error(self, message, code=1):
        print >>sys.stderr, message
        sys.exit(code)

    def get_filter(self, option_list):
        filters = {}
        delete_all = option_list.get('all')
        if delete_all:
            return filters

        is_migrating = option_list.get('is_migrating')
        if is_migrating is not None:
            filters['is_migrating'] = int(is_migrating)

        is_created = option_list.get('is_created')
        if is_created is not None:
            filters['is_created'] = int(is_created)

        has_errors = option_list.get('has_errors')
        if has_errors is not None:
            filters['has_errors'] = int(has_errors)

        migration_date = option_list.get('migration_date')
        if migration_date is not None:
            year, month, day = migration_date.split('/')
            date = datetime(year=int(year), month=int(month), day=int(day))
            filters['migration_date__lte'] = date

        content_type_id = option_list.get('content_type_id')
        if content_type_id is not None:
            filters['content_type__id'] = content_type_id
        if not filters:
            self.error(self.usage_str)
        return filters

    def handle(self, *args, **options):
        filters = self.get_filter(options)
        migrated_object = MigratedObject.objects.filter(**filters)
        print 'Deleting %s migrated object' % migrated_object.count()
        migrated_object.delete()
