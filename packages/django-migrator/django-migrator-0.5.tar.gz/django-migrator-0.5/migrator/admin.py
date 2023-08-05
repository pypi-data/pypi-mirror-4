from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from migrator.models import MigratedObject


class MigratedObjectAdmin(ModelAdmin):
    readonly_fields = ('migration_command', 'content_type', 'object_id',
                       'old_db_key', 'has_errors', 'migration_date',
                       'is_created', 'is_migrating', 'errors',
                       'migration_fields_used', 'object_name', 'object_url', )
    search_fields = ('object_name', )
    list_display = ('object_name', 'migration_date', 'object_id',
                    'old_db_key', 'migration_command', 'object_link',
                    'is_migrating', 'is_created', 'has_errors', )
    list_filter = ('is_migrating', 'has_errors', 'migration_command', )

    def object_link(self, obj):
        if obj.object_url is None:
            return ''
        return '<a href="%s">Link</a>' % obj.object_url
    object_link.allow_tags = True

admin.site.register(MigratedObject, MigratedObjectAdmin)
