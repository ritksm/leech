# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ShortenUrl'
        db.create_table('leech_shortenurl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.CharField')(null=True, max_length=32)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user_uuid', self.gf('django.db.models.fields.CharField')(null=True, max_length=64)),
        ))
        db.send_create_signal('leech', ['ShortenUrl'])

        # Adding model 'ClickLog'
        db.create_table('leech_clicklog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shorten_url', self.gf('django.db.models.fields.related.ForeignKey')(related_name='click_logs', to=orm['leech.ShortenUrl'])),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('remote_address', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('click_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('leech', ['ClickLog'])

        # Adding model 'ClickLogAttribute'
        db.create_table('leech_clicklogattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('click_log', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attributes', to=orm['leech.ClickLog'])),
            ('name', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('leech', ['ClickLogAttribute'])


    def backwards(self, orm):
        # Deleting model 'ShortenUrl'
        db.delete_table('leech_shortenurl')

        # Deleting model 'ClickLog'
        db.delete_table('leech_clicklog')

        # Deleting model 'ClickLogAttribute'
        db.delete_table('leech_clicklogattribute')


    models = {
        'leech.clicklog': {
            'Meta': {'object_name': 'ClickLog'},
            'click_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'shorten_url': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'click_logs'", 'to': "orm['leech.ShortenUrl']"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'leech.clicklogattribute': {
            'Meta': {'object_name': 'ClickLogAttribute'},
            'click_log': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attributes'", 'to': "orm['leech.ClickLog']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'leech.shortenurl': {
            'Meta': {'object_name': 'ShortenUrl'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '32'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_uuid': ('django.db.models.fields.CharField', [], {'null': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['leech']