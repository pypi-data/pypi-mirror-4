# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Campaign'
        db.create_table('feedback_campaign', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, primary_key=True)),
        ))
        db.send_create_signal('feedback', ['Campaign'])

        # Adding model 'Feedback'
        db.create_table('feedback_feedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('campaign', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['feedback.Campaign'], null=True)),
        ))
        db.send_create_signal('feedback', ['Feedback'])


    def backwards(self, orm):
        # Deleting model 'Campaign'
        db.delete_table('feedback_campaign')

        # Deleting model 'Feedback'
        db.delete_table('feedback_feedback')


    models = {
        'feedback.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'primary_key': 'True'})
        },
        'feedback.feedback': {
            'Meta': {'object_name': 'Feedback'},
            'campaign': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['feedback.Campaign']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['feedback']