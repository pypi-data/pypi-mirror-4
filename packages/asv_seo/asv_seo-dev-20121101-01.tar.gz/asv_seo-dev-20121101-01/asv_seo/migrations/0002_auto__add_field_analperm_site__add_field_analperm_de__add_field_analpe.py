# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'AnalPerm.site'
        db.add_column('asv_seo_analperm', 'site', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['sites.Site']), keep_default=False)

        # Adding field 'AnalPerm.de'
        db.add_column('asv_seo_analperm', 'de', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.date(2012, 3, 28), blank=True), keep_default=False)

        # Adding field 'AnalPerm.lm'
        db.add_column('asv_seo_analperm', 'lm', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.date(2012, 3, 28), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'AnalPerm.site'
        db.delete_column('asv_seo_analperm', 'site_id')

        # Deleting field 'AnalPerm.de'
        db.delete_column('asv_seo_analperm', 'de')

        # Deleting field 'AnalPerm.lm'
        db.delete_column('asv_seo_analperm', 'lm')


    models = {
        'asv_seo.analperm': {
            'Meta': {'ordering': "(u'site', u'system', u'name', u'de')", 'object_name': 'AnalPerm'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'de': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '512', 'db_index': 'True'}),
            'lm': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'system': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'})
        },
        'asv_seo.seo': {
            'Meta': {'ordering': "(u'content_type', u'de')", 'object_name': 'SEO'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'de': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_ru': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'keywords_ru': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'lm': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title_en': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'title_ru': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'asv_seo.seo4articles': {
            'Meta': {'ordering': "(u'content_type', u'de')", 'object_name': 'SEO4articles'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'de': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "u'ru'", 'max_length': '2', 'blank': 'True'}),
            'lm': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'asv_seo.webcounter': {
            'Meta': {'ordering': "(u'lm',)", 'object_name': 'WebCounter'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'code': ('django.db.models.fields.TextField', [], {}),
            'de': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lm': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
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

    complete_apps = ['asv_seo']
