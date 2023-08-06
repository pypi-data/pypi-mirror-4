# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'User.name'
        db.alter_column('facebook_users_user', 'name', self.gf('django.db.models.fields.CharField')(max_length=300))
    def backwards(self, orm):

        # Changing field 'User.name'
        db.alter_column('facebook_users_user', 'name', self.gf('django.db.models.fields.CharField')(max_length=200))
    models = {
        'facebook_users.user': {
            'Meta': {'ordering': "['name']", 'object_name': 'User'},
            'graph_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['facebook_users']