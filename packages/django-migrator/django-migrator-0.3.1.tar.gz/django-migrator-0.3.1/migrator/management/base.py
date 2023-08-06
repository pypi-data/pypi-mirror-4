# -*- coding: utf-8 -*-

import sys
import time
from datetime import datetime
from optparse import make_option
import pprint

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand
from django.db import models

from migrator.models import MigratedObject
from migrator.exceptions import MigrationError


class MigrationCommand(BaseCommand):

    MODE_DEFAULT = 'abortifempty'

    option_list = BaseCommand.option_list + (
            make_option('-d', '--database', default=settings.MIGRATION_DATABASE, dest='database',
                    help='Migration database'),
            make_option('-H', '--host', default=settings.MIGRATION_HOST, dest='host',
                    help='Migration database host'),
            make_option('-u', '--user', default=settings.MIGRATION_USER, dest='user',
                    help='Migration database user'),
            make_option('-p', '--password', default=settings.MIGRATION_PASSWORD, dest='password',
                    help='Migration database password'),
            make_option('-l', '--limit', default=0, dest='limit',
                    help='Max objects to migrate, if --limit 0 or no limit defined, there will be no limit.'),
            make_option('-f', '--from-date', default=None, dest='from_date',
                    help='Migrate only from date. Format: YYYY-MM-DD'),
            make_option('-e', '--only-with-errors', action='store_true', default=False, dest='only_with_errors',
                    help='Migrate only objects which had an error in previous migration'),
            make_option('-n', '--only-new-objects', action='store_true', default=False, dest='only_new_objects',
                    help='Migrate only new objects (not migrated in previous migrations)'),
            make_option('-a', '--all', action='store_true', default=False, dest='all_objects',
                    help='Migrate all objects including news'),
            make_option('-o', '--no-interactive', action='store_true', default=False, dest='no_interactive',
                    help='Tells Django to NOT prompt the user for input of any kind.'),
            make_option('-r', '--register-only-with-errors', action='store_true', default=False, dest='register_only_with_errors',
                    help='Only register migrations with errors'),
    )

    def _log(self, msg, verbosity):
        if self.verbosity >= verbosity:
            print msg

    def ask_yesno_question(self, question, default_answer='no'):
        if self.no_interactive:
            return default_answer
        while True:
            prompt = '%s: (yes/no) [%s]: ' % (question, default_answer)
            answer = raw_input(prompt).strip()
            if answer == '':
                return default_answer
            elif answer in ('yes', 'no'):
                return answer
            else:
                print 'Please answer yes or no'

    def _check_previous_migrations_question(self):
        return self.ask_yesno_question(
                    'There is half migrated objects in this database, do you want to continue?')

    def _check_previous_migrations(self):
        not_finished_migrations = MigratedObject.objects.filter(is_migrating=True)
        if not_finished_migrations:
            answer = self._check_previous_migrations_question()
            if answer == 'no':
                self.info('Migration aborted')
                sys.exit(1)
            self.info('Deleting previously not finished migrations...')
            not_finished_migrations.delete()

    def debug(self, msg):
        self._log('\t' + msg, 2)

    def info(self, msg):
        self._log(msg, 1)

    def handle(self, *args, **options):
        self.verbosity = int(options.get('verbosity'))
        self.database = options.get('database')
        self.host = options.get('host')
        self.limit = int(options.get('limit'))
        self.user = options.get('user')
        self.password = options.get('password')
        self.only_with_errors = options.get('only_with_errors')
        self.only_new_objects = options.get('only_new_objects')
        self.all_objects = options.get('all_objects')
        self.no_interactive = options.get('no_interactive')
        self.register_only_with_errors = options.get('register_only_with_errors')
        if options.get('from_date'):
            self.from_date = datetime(*time.strptime(options.get('from_date'), '%Y-%m-%d')[:3])
        else:
            self.from_date = None
        self.migration_date = datetime.now()

        self.info('Begin migration...')
        self.info('Connecting to "%s" SQL Server Database in %s host...' % (self.database, self.host))
        self.start_connection()
        self.info('Connected.')
        self.info('Begin data migration...\n')
        if self.only_with_errors:
            self.info('NOTE: only migrating objects which previous migrations had errors')
        self.handle_migrationcommand(self, *args, **options)
        self.info('\nMigration finished. Closing connection...')
        self.close_connection()
        self.info('Done.')

    def handle_migrationcommand(self, *args, **options):
        """
        May be overriden in subclasses to customize migration process
        """
        self._check_previous_migrations()
        roadmap = self.get_roadmap()
        for migration_step in roadmap:
            source_name = migration_step['source_name']
            model_name = migration_step['model_name']
            limit = migration_step.get('limit', self.limit)
            source_fields = migration_step['source_fields']
            migration_fields = migration_step['migration_fields']
            self.info('Begin migration of %s source...' % source_name)
            self.migrate_model(source_name, model_name, limit, source_fields, migration_fields, migration_step)
            self.info('Finished migration of %s source.' % source_name)

    def migrate_model(self, source_name, model_name, limit, source_fields, migration_fields, migration_step):
        """
        May be overriden in subclasses to customize migration process
        """
        source_fields = list(source_fields)
        old_pk_name = migration_step['old_pk_name']
        if old_pk_name not in source_fields:
            source_fields.insert(0, source_fields)
        source_fields += [d['source'] for d in migration_fields if d['source'] not in source_fields]
        source_results = self.get_source_results(source_name, source_fields, limit)
        model = self.get_model(model_name)
        save_empty_object = migration_step.get('save_empty_object', True)
        for i, source_data in enumerate(source_results):
            migrated_data_id = int(source_data[old_pk_name])
            is_migrated, obj = self.migrated_data_info(source_data, model)
            if is_migrated:
                self.debug('Do not migrate "%s". Already migrated.' % obj)
            else:
                if obj is not None and self.only_with_errors:
                    try:
                        mo = MigratedObject.objects.last_migration(obj)
                        if not mo.has_errors:
                            continue  # only migrating objects with errors
                    except MigratedObject.DoesNotExist:
                        continue  # no migration means object was no migrated with error
                elif obj is not None and self.only_new_objects and \
                     MigratedObject.objects.object_migrations(obj).exists():
                    self.debug('%d. Skip "%s" object' % (i, obj))
                    continue  # no migration for non new objects
                if obj is None:
                    is_created = True
                    obj = self.create_object(model, source_data, migration_fields, save_empty_object)
                else:
                    is_created = False
                migration_mark = self.mark_migration_start(obj, migrated_data_id, is_created)
                self.update_object(obj, source_data, migration_fields, migration_mark)
                is_created_prefix = is_created and 'new ' or ''
                self.debug('%d. Migrated %s"%s" object' % (i, is_created_prefix, obj))
                self.save_object(obj)
                if is_created:
                    self.update_db(obj, source_data, source_name, old_pk_name, migration_mark)
                self.mark_migration_end(migration_mark, migration_fields)  # we will finish object migration

    def get_model(self, model_name):
        """
        Return Django model from a string like "app_name.model"
        """
        return models.get_model(*model_name.split('.'))

    def migrated_data_info(self, source_data, model):
        """
        Returns if source data has been migrated or not
        """
        obj = self.get_object_if_exists(source_data, model)
        if obj is None:
            return False, obj
        else:
            return self.is_updated_object(obj, source_data), obj

    def is_updated_object(self, obj, source_data):
        """
        May be overriden in subclasses to customize if a object is updated
        or has to be migrated
        """
        if self.from_date is None:
            return False
        try:
            last_migration = MigratedObject.objects.last_migration(obj)
        except MigratedObject.DoesNotExist:
            return False
        return self.from_date <= last_migration.migration_date

    def is_empty_value(self, value):
        if isinstance(value, bool):
            return False
        return not value

    def mark_migration_start(self, obj, migrated_data_id, is_created):
        """
        Mark object with "is migrating" info
        """
        ctype = ContentType.objects.get_for_model(obj)
        migration_mark = MigratedObject.objects.create(
            content_type=ctype,
            object_id=obj.pk,
            is_migrating=True,  # maybe the object gets half migrated
            is_created=is_created,
            old_db_key=migrated_data_id,  # link to old database object,
            migration_date=self.migration_date,
            migration_command=self.get_migration_command(),
        )
        return migration_mark

    def mark_migration_end(self, migration_mark, migration_fields):
        """
        Unmark object with a "is migrating" flag.
        """
        if migration_mark.has_errors or not self.register_only_with_errors:
            migration_mark.is_migrating = False
            migration_mark.migration_fields_used = pprint.pformat(migration_fields)
            migration_mark.save()
        else:
            migration_mark.delete()

    def get_migration_command(self):
        return self.__class__.__module__

    def create_object(self, model, source_data, migration_fields, save_empty_object):
        """
        Create a new migrated object.
        """
        obj = model()  # a empty object which we mark is migrating right now
        if save_empty_object:
            self.save_object(obj)
        return obj

    def update_object(self, obj, source_data, migration_fields, migration_mark):
        """
        Create a existing object.
        """
        for field_mapping in migration_fields:
            try:
                source_field = field_mapping['source']
                field_name = field_mapping.get('destination', None)
                getter_name = field_mapping.get('getter', None)
                if getter_name:
                    getter_func = getattr(self, getter_name)
                else:
                    getter_func = self.getter
                value = getter_func(source_field, source_data)
                filters = field_mapping.get('filters', ())
                for filter_name in filters:
                    filter_func = getattr(self, filter_name)
                    value = filter_func(value)
                mode = field_mapping.get('mode', self.MODE_DEFAULT)
                if mode not in ('overwrite', 'abortifempty', 'onlyifcreated'):
                    raise ImproperlyConfigured('"mode" value has to be either'
                                               ' "abortifempty", "overwrite"'
                                               ' or "onlyifcreated"')
                if mode == 'abortifempty' and self.is_empty_value(value) or \
                mode == 'onlyifcreated' and not migration_mark.is_created:
                    # abort setting this field because value is empty
                    # we leave its previous object value
                    continue
                setter_name = field_mapping.get('setter', None)
                if setter_name:
                    setter_func = getattr(self, setter_name)
                    setter_func(obj, value)
                elif field_name:
                    self.setter(obj, field_name, value)
                else:
                    raise ImproperlyConfigured('You have to define either "destination" or "setter" in migration_fields')
            except MigrationError, e:
                self.info('  -> Error migrating "%s".' % obj)
                migration_mark.has_errors = True
                migration_mark.errors += u'\n' + e.message

    def getter(self, field_name, source_data):
        """
        Get an attribute from source data
        """
        return source_data[field_name]

    def setter(self, obj, field_name, value):
        """
        Set an attribute to the migrated object
        """
        setattr(obj, field_name, value)

    def save_object(self, obj):
        """
        Save object in tourism database.
        """
        obj.save()

    # ----- default filters  -----

    def filter_strip(self, value):
        if value is not None:
            value = value.strip()
        return value

    # ----- methods which are mandatory to be implemented in subclasses -----

    def start_connection(self):
        """
        Must be overriden in subclasses. self.connection has to be defined and connected
        """
        raise NotImplementedError()

    def close_connection(self):
        """
        Must be overriden in subclasses. self.connection has to be closed
        """
        raise NotImplementedError()

    def get_roadmap(self):
        """
        Must be overriden in subclasses. Returns a list of dictionaries which
        is a guide in migration proccess. The format must be::
        (
         {
            'source_name': 'GR_HOTELES_PENSIONES',
            'model_name': 'accommodation.accommodation',
            'limit': 10, # optional key. By default will be global limit
            'source_fields': ('id_cms', ),
            'old_pk_name': 'id',
            'save_empty_object': False, # save a new empty object after creation or not (default is True)
            'migration_fields': (
                {'source': 'denominacion', 'destination': 'name'},
                {'source': 'categoria', 'destination': 'category', 'getter': 'get_category'},
                {'source': 'email1', 'setter': 'set_email1', 'mode': 'overwrite'},
                {'source': 'phone1', 'filters': ('filter_strip', ), 'setter': 'set_phone1'},
            ),
         }, ...
        )
        Notes about previous example:
         * ``save_empty_object`` is saving object just after creation. Usually
           is needed because FK definitions need a object stored in database.
         * ``mode`` is the way value is set in object, with these two possible values:
           * 'abortifempty': if value we got is empty, object is remain
             untouched, the default value.
           * 'overwrite': object is always updated with value, even it's empty
           * 'onlyifcreated': object will be updated only when creating object
        """
        raise NotImplementedError()

    def get_source_results(self, source_name, source_fields, limit):
        """
        Returns a generator of source data, which is a list of dictionaries with the data to migrate
        """
        raise NotImplementedError()

    def get_object_if_exists(self, source_data, model):
        """
        Returns the object existing in tourism database or None
        """
        raise NotImplementedError()

    def update_db(self, obj, source_data, source_name, old_pk_name, migration_mark):
        """
        Update db
        """
        raise NotImplementedError()
