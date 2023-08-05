# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncomingMessage'
        db.create_table('fa_incomingmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('send_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('transport', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fa', ['IncomingMessage'])

        # Adding model 'OutgoingMessage'
        db.create_table('fa_outgoingmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('target', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('transport', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('fa', ['OutgoingMessage'])


    def backwards(self, orm):
        # Deleting model 'IncomingMessage'
        db.delete_table('fa_incomingmessage')

        # Deleting model 'OutgoingMessage'
        db.delete_table('fa_outgoingmessage')


    models = {
        'fa.incomingmessage': {
            'Meta': {'object_name': 'IncomingMessage'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'send_time': ('django.db.models.fields.DateTimeField', [], {}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'transport': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fa.outgoingmessage': {
            'Meta': {'object_name': 'OutgoingMessage'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'target': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'transport': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['fa']