# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('collection_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sort_index', self.gf('django.db.models.fields.IntegerField')()),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_special', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('collection', ['Category'])

        # Adding model 'Product'
        db.create_table('collection_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['collection.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('width', self.gf('django.db.models.fields.FloatField')()),
            ('height', self.gf('django.db.models.fields.FloatField')()),
            ('depth', self.gf('django.db.models.fields.FloatField')()),
            ('weight', self.gf('django.db.models.fields.FloatField')()),
            ('price_gbp', self.gf('django.db.models.fields.FloatField')()),
            ('price_usd', self.gf('django.db.models.fields.FloatField')()),
            ('price_eur', self.gf('django.db.models.fields.FloatField')()),
            ('in_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('num_views', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('collection', ['Product'])

        # Adding model 'Photo'
        db.create_table('collection_photo', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('orientation', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('collection', ['Photo'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('collection_category')

        # Deleting model 'Product'
        db.delete_table('collection_product')

        # Deleting model 'Photo'
        db.delete_table('collection_photo')


    models = {
        'collection.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['collection.Category']"}),
            'depth': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_date': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'num_views': ('django.db.models.fields.IntegerField', [], {}),
            'price_eur': ('django.db.models.fields.FloatField', [], {}),
            'price_gbp': ('django.db.models.fields.FloatField', [], {}),
            'price_usd': ('django.db.models.fields.FloatField', [], {}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'weight': ('django.db.models.fields.FloatField', [], {}),
            'width': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['collection']
