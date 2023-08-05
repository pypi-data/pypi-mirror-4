# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Photo.image'
        db.alter_column('collection_photo', 'image', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100, null=True))

        # Changing field 'Product.price_usd'
        db.alter_column('collection_product', 'price_usd', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Product.weight'
        db.alter_column('collection_product', 'weight', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Product.price_gbp'
        db.alter_column('collection_product', 'price_gbp', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Product.description'
        db.alter_column('collection_product', 'description', self.gf('django.db.models.fields.TextField')(max_length=401))

        # Changing field 'Product.depth'
        db.alter_column('collection_product', 'depth', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Product.height'
        db.alter_column('collection_product', 'height', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Product.width'
        db.alter_column('collection_product', 'width', self.gf('django.db.models.fields.FloatField')(null=True))

        # Changing field 'Product.price_eur'
        db.alter_column('collection_product', 'price_eur', self.gf('django.db.models.fields.FloatField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'Photo.image'
        db.alter_column('collection_photo', 'image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True))

        # Changing field 'Product.price_usd'
        db.alter_column('collection_product', 'price_usd', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'Product.weight'
        db.alter_column('collection_product', 'weight', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'Product.price_gbp'
        db.alter_column('collection_product', 'price_gbp', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'Product.description'
        db.alter_column('collection_product', 'description', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Product.depth'
        db.alter_column('collection_product', 'depth', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'Product.height'
        db.alter_column('collection_product', 'height', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'Product.width'
        db.alter_column('collection_product', 'width', self.gf('django.db.models.fields.FloatField')(default=0))

        # Changing field 'Product.price_eur'
        db.alter_column('collection_product', 'price_eur', self.gf('django.db.models.fields.FloatField')(default=0))


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
            'depth': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '401'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'height': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 4, 4, 21, 11, 56, 475040)'}),
            'live': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'num_views': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price_eur': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'price_gbp': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'price_usd': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'width': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        }
    }

    complete_apps = ['collection']
