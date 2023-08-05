# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table('sources_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.Language'])),
            ('source', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('sources', ['Source'])

        # Adding model 'Language'
        db.create_table('sources_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('cmd_compiler', self.gf('django.db.models.fields.TextField')()),
            ('cmd_starter', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sources', ['Language'])

        # Adding model 'LanguageExtension'
        db.create_table('sources_languageextension', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.Language'])),
            ('extension', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
        ))
        db.send_create_signal('sources', ['LanguageExtension'])


    def backwards(self, orm):
        # Deleting model 'Source'
        db.delete_table('sources_source')

        # Deleting model 'Language'
        db.delete_table('sources_language')

        # Deleting model 'LanguageExtension'
        db.delete_table('sources_languageextension')


    models = {
        'sources.language': {
            'Meta': {'object_name': 'Language'},
            'cmd_compiler': ('django.db.models.fields.TextField', [], {}),
            'cmd_starter': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'sources.languageextension': {
            'Meta': {'object_name': 'LanguageExtension'},
            'extension': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Language']"})
        },
        'sources.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sources.Language']"}),
            'source': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['sources']