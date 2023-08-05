# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Categories'
        db.create_table('rshop_categories', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('rshop', ['Categories'])

        # Adding model 'Products'
        db.create_table('rshop_products', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='category', to=orm['rshop.Categories'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('hits', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('rshop', ['Products'])

        # Adding model 'Images'
        db.create_table('rshop_images', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['rshop.Products'])),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('rshop', ['Images'])


    def backwards(self, orm):
        # Deleting model 'Categories'
        db.delete_table('rshop_categories')

        # Deleting model 'Products'
        db.delete_table('rshop_products')

        # Deleting model 'Images'
        db.delete_table('rshop_images')


    models = {
        'rshop.categories': {
            'Meta': {'object_name': 'Categories'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'rshop.images': {
            'Meta': {'object_name': 'Images'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['rshop.Products']"}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'rshop.products': {
            'Meta': {'object_name': 'Products'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'category'", 'to': "orm['rshop.Categories']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'hits': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['rshop']