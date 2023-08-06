# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('facebook_users_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('graph_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('facebook_users', ['User'])

    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('facebook_users_user')

    models = {
        'facebook_users.user': {
            'Meta': {'ordering': "['name']", 'object_name': 'User'},
            'graph_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['facebook_users']