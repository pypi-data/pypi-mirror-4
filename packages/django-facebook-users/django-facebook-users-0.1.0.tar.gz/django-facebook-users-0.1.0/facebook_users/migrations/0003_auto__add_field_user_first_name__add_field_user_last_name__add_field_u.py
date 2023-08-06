# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'User.first_name'
        db.add_column('facebook_users_user', 'first_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.last_name'
        db.add_column('facebook_users_user', 'last_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.middle_name'
        db.add_column('facebook_users_user', 'middle_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.gender'
        db.add_column('facebook_users_user', 'gender',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=10),
                      keep_default=False)

        # Adding field 'User.locale'
        db.add_column('facebook_users_user', 'locale',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=5),
                      keep_default=False)

        # Adding field 'User.link'
        db.add_column('facebook_users_user', 'link',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.cover'
        db.add_column('facebook_users_user', 'cover',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.username'
        db.add_column('facebook_users_user', 'username',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.third_party_id'
        db.add_column('facebook_users_user', 'third_party_id',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.updated_time'
        db.add_column('facebook_users_user', 'updated_time',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(1970, 1, 1, 0, 0)),
                      keep_default=False)

        # Adding field 'User.email'
        db.add_column('facebook_users_user', 'email',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.timezone'
        db.add_column('facebook_users_user', 'timezone',
                      self.gf('django.db.models.fields.IntegerField')(null=True),
                      keep_default=False)

        # Adding field 'User.bio'
        db.add_column('facebook_users_user', 'bio',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'User.birthday'
        db.add_column('facebook_users_user', 'birthday',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=300),
                      keep_default=False)

        # Adding field 'User.languages'
        db.add_column('facebook_users_user', 'languages',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.installed'
        db.add_column('facebook_users_user', 'installed',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.verified'
        db.add_column('facebook_users_user', 'verified',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'User.currency'
        db.add_column('facebook_users_user', 'currency',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.devices'
        db.add_column('facebook_users_user', 'devices',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.education'
        db.add_column('facebook_users_user', 'education',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.hometown'
        db.add_column('facebook_users_user', 'hometown',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.interested_in'
        db.add_column('facebook_users_user', 'interested_in',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.location'
        db.add_column('facebook_users_user', 'location',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.payment_pricepoints'
        db.add_column('facebook_users_user', 'payment_pricepoints',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.favorite_athletes'
        db.add_column('facebook_users_user', 'favorite_athletes',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.favorite_teams'
        db.add_column('facebook_users_user', 'favorite_teams',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.political'
        db.add_column('facebook_users_user', 'political',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.picture'
        db.add_column('facebook_users_user', 'picture',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.quotes'
        db.add_column('facebook_users_user', 'quotes',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.relationship_status'
        db.add_column('facebook_users_user', 'relationship_status',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.religion'
        db.add_column('facebook_users_user', 'religion',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.security_settings'
        db.add_column('facebook_users_user', 'security_settings',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.significant_other'
        db.add_column('facebook_users_user', 'significant_other',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.video_upload_limits'
        db.add_column('facebook_users_user', 'video_upload_limits',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

        # Adding field 'User.website'
        db.add_column('facebook_users_user', 'website',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'User.work'
        db.add_column('facebook_users_user', 'work',
                      self.gf('annoying.fields.JSONField')(max_length=500, null=True),
                      keep_default=False)

    def backwards(self, orm):
        # Deleting field 'User.first_name'
        db.delete_column('facebook_users_user', 'first_name')

        # Deleting field 'User.last_name'
        db.delete_column('facebook_users_user', 'last_name')

        # Deleting field 'User.middle_name'
        db.delete_column('facebook_users_user', 'middle_name')

        # Deleting field 'User.gender'
        db.delete_column('facebook_users_user', 'gender')

        # Deleting field 'User.locale'
        db.delete_column('facebook_users_user', 'locale')

        # Deleting field 'User.link'
        db.delete_column('facebook_users_user', 'link')

        # Deleting field 'User.cover'
        db.delete_column('facebook_users_user', 'cover')

        # Deleting field 'User.username'
        db.delete_column('facebook_users_user', 'username')

        # Deleting field 'User.third_party_id'
        db.delete_column('facebook_users_user', 'third_party_id')

        # Deleting field 'User.updated_time'
        db.delete_column('facebook_users_user', 'updated_time')

        # Deleting field 'User.email'
        db.delete_column('facebook_users_user', 'email')

        # Deleting field 'User.timezone'
        db.delete_column('facebook_users_user', 'timezone')

        # Deleting field 'User.bio'
        db.delete_column('facebook_users_user', 'bio')

        # Deleting field 'User.birthday'
        db.delete_column('facebook_users_user', 'birthday')

        # Deleting field 'User.languages'
        db.delete_column('facebook_users_user', 'languages')

        # Deleting field 'User.installed'
        db.delete_column('facebook_users_user', 'installed')

        # Deleting field 'User.verified'
        db.delete_column('facebook_users_user', 'verified')

        # Deleting field 'User.currency'
        db.delete_column('facebook_users_user', 'currency')

        # Deleting field 'User.devices'
        db.delete_column('facebook_users_user', 'devices')

        # Deleting field 'User.education'
        db.delete_column('facebook_users_user', 'education')

        # Deleting field 'User.hometown'
        db.delete_column('facebook_users_user', 'hometown')

        # Deleting field 'User.interested_in'
        db.delete_column('facebook_users_user', 'interested_in')

        # Deleting field 'User.location'
        db.delete_column('facebook_users_user', 'location')

        # Deleting field 'User.payment_pricepoints'
        db.delete_column('facebook_users_user', 'payment_pricepoints')

        # Deleting field 'User.favorite_athletes'
        db.delete_column('facebook_users_user', 'favorite_athletes')

        # Deleting field 'User.favorite_teams'
        db.delete_column('facebook_users_user', 'favorite_teams')

        # Deleting field 'User.political'
        db.delete_column('facebook_users_user', 'political')

        # Deleting field 'User.picture'
        db.delete_column('facebook_users_user', 'picture')

        # Deleting field 'User.quotes'
        db.delete_column('facebook_users_user', 'quotes')

        # Deleting field 'User.relationship_status'
        db.delete_column('facebook_users_user', 'relationship_status')

        # Deleting field 'User.religion'
        db.delete_column('facebook_users_user', 'religion')

        # Deleting field 'User.security_settings'
        db.delete_column('facebook_users_user', 'security_settings')

        # Deleting field 'User.significant_other'
        db.delete_column('facebook_users_user', 'significant_other')

        # Deleting field 'User.video_upload_limits'
        db.delete_column('facebook_users_user', 'video_upload_limits')

        # Deleting field 'User.website'
        db.delete_column('facebook_users_user', 'website')

        # Deleting field 'User.work'
        db.delete_column('facebook_users_user', 'work')

    models = {
        'facebook_users.user': {
            'Meta': {'ordering': "['name']", 'object_name': 'User'},
            'bio': ('django.db.models.fields.TextField', [], {}),
            'birthday': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'cover': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'currency': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'devices': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'education': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'favorite_athletes': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'favorite_teams': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'graph_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'hometown': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installed': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'interested_in': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'languages': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '300'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'location': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'payment_pricepoints': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'picture': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'political': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'quotes': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'relationship_status': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'religion': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'security_settings': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'significant_other': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'third_party_id': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'timezone': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'video_upload_limits': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'work': ('annoying.fields.JSONField', [], {'max_length': '500', 'null': 'True'})
        }
    }

    complete_apps = ['facebook_users']