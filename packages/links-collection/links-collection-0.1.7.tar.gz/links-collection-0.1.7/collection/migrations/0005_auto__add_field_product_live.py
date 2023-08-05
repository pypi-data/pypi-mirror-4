# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Product.live'
        db.add_column('collection_product', 'live', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Product.live'
        db.delete_column('collection_product', 'live')


    models = {
        'collection.category': {
            'Meta': {'ordering': "['sort_index']", 'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction_text': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'is_special': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sort_index': ('django.db.models.fields.IntegerField', [], {})
        },
        'collection.photo': {
            'Meta': {'object_name': 'Photo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'orientation': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'collection.product': {
            'Meta': {'ordering': "['-in_date']", 'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'products'", 'to': "orm['collection.Category']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_date': ('django.db.models.fields.DateTimeField', [], {}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'num_views': ('django.db.models.fields.IntegerField', [], {}),
            'price_eur': ('django.db.models.fields.FloatField', [], {}),
            'price_gbp': ('django.db.models.fields.FloatField', [], {}),
            'price_usd': ('django.db.models.fields.FloatField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'weight': ('django.db.models.fields.FloatField', [], {}),
            'width': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['collection']
