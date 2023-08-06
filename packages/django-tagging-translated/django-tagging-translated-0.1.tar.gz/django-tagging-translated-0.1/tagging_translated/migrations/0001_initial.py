# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TagTitle'
        db.create_table('tagging_translated_tagtitle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('trans_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tagging.Tag'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('tagging_translated', ['TagTitle'])


    def backwards(self, orm):
        # Deleting model 'TagTitle'
        db.delete_table('tagging_translated_tagtitle')


    models = {
        'tagging.tag': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'tagging_translated.tagtitle': {
            'Meta': {'object_name': 'TagTitle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tagging.Tag']"}),
            'trans_name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['tagging_translated']