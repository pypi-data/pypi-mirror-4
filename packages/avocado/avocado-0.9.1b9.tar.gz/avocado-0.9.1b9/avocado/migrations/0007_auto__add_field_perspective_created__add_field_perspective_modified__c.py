# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Perspective.created'
        db.add_column('avocado_perspective', 'created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 9, 17, 36, 9, 293249)), keep_default=False)

        # Adding field 'Perspective.modified'
        db.add_column('avocado_perspective', 'modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 9, 17, 36, 17, 501402)), keep_default=False)

        # Changing field 'Perspective.store'
        db.alter_column('avocado_perspective', 'store', self.gf('avocado.store.fields.JSONField')(editable=False))

        # Adding field 'Report.created'
        db.add_column('avocado_report', 'created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 9, 17, 36, 22, 805747)), keep_default=False)

        # Adding field 'Report.modified'
        db.add_column('avocado_report', 'modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 9, 17, 36, 32, 445973)), keep_default=False)

        # Adding field 'Scope.created'
        db.add_column('avocado_scope', 'created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 9, 17, 36, 42, 598399)), keep_default=False)

        # Adding field 'Scope.modified'
        db.add_column('avocado_scope', 'modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2011, 8, 9, 17, 36, 46, 950524)), keep_default=False)

        # Changing field 'Scope.store'
        db.alter_column('avocado_scope', 'store', self.gf('avocado.store.fields.JSONField')(editable=False))


    def backwards(self, orm):
        
        # Deleting field 'Perspective.created'
        db.delete_column('avocado_perspective', 'created')

        # Deleting field 'Perspective.modified'
        db.delete_column('avocado_perspective', 'modified')

        # Changing field 'Perspective.store'
        db.alter_column('avocado_perspective', 'store', self.gf('avocado.store.fields.JSONField')(null=True, editable=False))

        # Deleting field 'Report.created'
        db.delete_column('avocado_report', 'created')

        # Deleting field 'Report.modified'
        db.delete_column('avocado_report', 'modified')

        # Deleting field 'Scope.created'
        db.delete_column('avocado_scope', 'created')

        # Deleting field 'Scope.modified'
        db.delete_column('avocado_scope', 'modified')

        # Changing field 'Scope.store'
        db.alter_column('avocado_scope', 'store', self.gf('avocado.store.fields.JSONField')(null=True, editable=False))


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
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'order': ('django.db.models.fields.FloatField', [], {'default': '0'}),
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
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'translator': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'avocado.perspective': {
            'Meta': {'object_name': 'Perspective'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'definition': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'store': ('avocado.store.fields.JSONField', [], {'editable': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 8, 9, 17, 35, 47, 433504)'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'avocado.report': {
            'Meta': {'object_name': 'Report'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'perspective': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Perspective']", 'unique': 'True'}),
            'scope': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['avocado.Scope']", 'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'avocado.scope': {
            'Meta': {'object_name': 'Scope'},
            'cnt': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'definition': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'store': ('avocado.store.fields.JSONField', [], {'editable': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2011, 8, 9, 17, 35, 47, 433504)'}),
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
