# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field sites on 'Field'
        db.create_table('avocado_field_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('field', models.ForeignKey(orm['avocado.field'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('avocado_field_sites', ['field_id', 'site_id'])

        # Changing field 'Field.status'
        db.alter_column('avocado_field', 'status', self.gf('django.db.models.fields.CharField')(max_length=40, null=True))

        # Changing field 'Field.reviewed'
        db.alter_column('avocado_field', 'reviewed', self.gf('django.db.models.fields.DateTimeField')(null=True))


    def backwards(self, orm):
        
        # Removing M2M table for field sites on 'Field'
        db.delete_table('avocado_field_sites')

        # User chose to not deal with backwards NULL issues for 'Field.status'
        raise RuntimeError("Cannot reverse this migration. 'Field.status' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Field.reviewed'
        raise RuntimeError("Cannot reverse this migration. 'Field.reviewed' and its values cannot be restored.")


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'avocado.category': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Category'},
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['avocado.Category']"})
        },
        'avocado.column': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Column'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Category']", 'null': 'True', 'blank': 'True'}),
            'csv_fmtr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['avocado.Field']", 'through': "orm['avocado.ColumnField']", 'symmetrical': 'False'}),
            'html_fmtr': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reviewed': ('django.db.models.fields.DateTimeField', [], {}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'avocado.columnfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'ColumnField'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conceptfields'", 'to': "orm['avocado.Column']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'avocado.criterion': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Criterion'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Category']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fields': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['avocado.Field']", 'through': "orm['avocado.CriterionField']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'reviewed': ('django.db.models.fields.DateTimeField', [], {}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'viewset': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'avocado.criterionfield': {
            'Meta': {'ordering': "('order',)", 'object_name': 'CriterionField'},
            'concept': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'conceptfields'", 'to': "orm['avocado.Criterion']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['avocado.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'avocado.field': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_name', 'model_name', 'field_name'),)", 'object_name': 'Field'},
            'app_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'chart_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'chart_xaxis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'chart_yaxis': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'choices_handler': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enable_choices': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'reviewed': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'search_doc': ('django.db.models.fields.TextField', [], {'null': 'True', 'db_index': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'avocado.perspective': {
            'Meta': {'object_name': 'Perspective'},
            'definition': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'store': ('avocado.store.fields.PickledField', [], {'null': 'True', 'editable': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 3, 1, 9, 16, 20, 808748)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'avocado.report': {
            'Meta': {'object_name': 'Report'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'perspective': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Perspective']", 'unique': 'True'}),
            'scope': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Scope']", 'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'avocado.scope': {
            'Meta': {'object_name': 'Scope'},
            'cnt': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'definition': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'store': ('avocado.store.fields.PickledField', [], {'null': 'True', 'editable': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 3, 1, 9, 16, 20, 808748)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['avocado']
