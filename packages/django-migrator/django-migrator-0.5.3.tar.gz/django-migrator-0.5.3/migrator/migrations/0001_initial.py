from south.db import db


class Migration:

    def forwards(self, orm):
        # Adding model 'MigratedObject'
        db.create_table('migrator_migratedobject', (
            ('id', orm['migrator.MigratedObject:id']),
            ('content_type', orm['migrator.MigratedObject:content_type']),
            ('object_id', orm['migrator.MigratedObject:object_id']),
            ('old_db_key', orm['migrator.MigratedObject:old_db_key']),
            ('migration_date', orm['migrator.MigratedObject:migration_date']),
            ('is_migrating', orm['migrator.MigratedObject:is_migrating']),
        ))
        db.send_create_signal('migrator', ['MigratedObject'])

    def backwards(self, orm):
        # Deleting model 'MigratedObject'
        db.delete_table('migrator_migratedobject')

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
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'old_db_key': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'null': 'True', 'blank': 'True'}),
        },
    }

    complete_apps = ['migrator']
