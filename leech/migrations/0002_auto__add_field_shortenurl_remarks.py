# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ShortenUrl.remarks'
        db.add_column('leech_shortenurl', 'remarks',
                      self.gf('django.db.models.fields.CharField')(default='', blank=True, max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ShortenUrl.remarks'
        db.delete_column('leech_shortenurl', 'remarks')


    models = {
        'leech.clicklog': {
            'Meta': {'object_name': 'ClickLog'},
            'click_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'shorten_url': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['leech.ShortenUrl']", 'related_name': "'click_logs'"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'leech.clicklogattribute': {
            'Meta': {'object_name': 'ClickLogAttribute'},
            'click_log': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['leech.ClickLog']", 'related_name': "'attributes'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'leech.shortenurl': {
            'Meta': {'object_name': 'ShortenUrl'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remarks': ('django.db.models.fields.CharField', [], {'default': "''", 'blank': 'True', 'max_length': '255'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_uuid': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'})
        }
    }

    complete_apps = ['leech']