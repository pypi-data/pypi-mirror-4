from south.db import db


class Migration:

    def forwards(self, orm):
        "Write your forwards migration here"
        db.add_column('migrator_migratedobject', 'migration_fields_used', orm['migrator.migratedobject:migration_fields_used'])

    def backwards(self, orm):
        "Write your backwards migration here"

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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_migrating': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'migration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'migration_fields_used': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'old_db_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
        },
    }

    complete_apps = ['migrator']
