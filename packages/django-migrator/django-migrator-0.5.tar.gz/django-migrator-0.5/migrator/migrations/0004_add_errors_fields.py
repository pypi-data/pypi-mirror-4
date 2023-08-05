
from south.db import db


class Migration:

    def forwards(self, orm):
        # Adding field 'MigratedObject.errors'
        db.add_column('migrator_migratedobject', 'errors', orm['migrator.migratedobject:errors'])
        # Adding field 'MigratedObject.has_errors'
        db.add_column('migrator_migratedobject', 'has_errors', orm['migrator.migratedobject:has_errors'])

    def backwards(self, orm):
        # Deleting field 'MigratedObject.errors'
        db.delete_column('migrator_migratedobject', 'errors')
        # Deleting field 'MigratedObject.has_errors'
        db.delete_column('migrator_migratedobject', 'has_errors')

    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
        },
        'migrator.migratedobject': {
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'errors': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'has_errors': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_migrating': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'migration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'migration_fields_used': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'object_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'db_index': 'True'}),
            'old_db_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'db_index': 'True'}),
        },
    }

    complete_apps = ['migrator']
