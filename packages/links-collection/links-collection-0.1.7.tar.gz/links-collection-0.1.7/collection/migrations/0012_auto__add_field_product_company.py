# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Product.company'
        db.add_column('collection_product', 'company',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='products', null=True, to=orm['luxuryadmin.Company']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Product.company'
        db.delete_column('collection_product', 'company_id')


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
            'Meta': {'ordering': "['sort_index']", 'object_name': 'Photo'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'photos'", 'to': "orm['collection.Product']"}),
            'sort_index': ('django.db.models.fields.IntegerField', [], {})
        },
        'collection.product': {
            'Meta': {'ordering': "['-in_date']", 'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'all_products'", 'to': "orm['collection.Category']"}),
            'company': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'products'", 'null': 'True', 'to': "orm['luxuryadmin.Company']"}),
            'depth': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '401'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 8, 22, 0, 0)'}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'num_views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price_eur': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'price_gbp': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'price_usd': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '10', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'sold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'luxuryadmin.company': {
            'Meta': {'object_name': 'Company'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landline': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['collection']