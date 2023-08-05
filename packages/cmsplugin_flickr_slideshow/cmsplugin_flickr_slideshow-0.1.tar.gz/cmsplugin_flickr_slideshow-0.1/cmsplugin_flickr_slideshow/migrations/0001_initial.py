# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FlickrSlideshow'
        db.create_table('cmsplugin_flickrslideshow', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['cms.CMSPlugin'], unique=True, primary_key=True)),
            ('flikr_id', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('flashvars', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('allowfullscreen', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(default=510)),
            ('height', self.gf('django.db.models.fields.IntegerField')(default=300)),
        ))
        db.send_create_signal('cmsplugin_flickr_slideshow', ['FlickrSlideshow'])


    def backwards(self, orm):
        # Deleting model 'FlickrSlideshow'
        db.delete_table('cmsplugin_flickrslideshow')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'cmsplugin_flickr_slideshow.flickrslideshow': {
            'Meta': {'object_name': 'FlickrSlideshow', 'db_table': "'cmsplugin_flickrslideshow'", '_ormbases': ['cms.CMSPlugin']},
            'allowfullscreen': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'flashvars': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'flikr_id': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '300'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '510'})
        }
    }

    complete_apps = ['cmsplugin_flickr_slideshow']