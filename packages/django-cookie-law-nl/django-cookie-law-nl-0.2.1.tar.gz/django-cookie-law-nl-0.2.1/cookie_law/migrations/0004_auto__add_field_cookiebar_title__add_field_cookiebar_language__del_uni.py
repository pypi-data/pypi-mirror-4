# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'CookieBar', fields ['use_this']
        db.delete_unique('cookie_law_cookiebar', ['use_this'])

        # Adding field 'CookieBar.title'
        db.add_column('cookie_law_cookiebar', 'title', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True), keep_default=False)

        # Adding field 'CookieBar.language'
        db.add_column('cookie_law_cookiebar', 'language', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=8, null=True, blank=True), keep_default=False)

        # Changing field 'CookieBar.link_name'
        db.alter_column('cookie_law_cookiebar', 'link_name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'CookieBar.link'
        db.alter_column('cookie_law_cookiebar', 'link', self.gf('django.db.models.fields.URLField')(max_length=255, null=True))

        # Adding unique constraint on 'CookieBar', fields ['use_this', 'language']
        db.create_unique('cookie_law_cookiebar', ['use_this', 'language'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'CookieBar', fields ['use_this', 'language']
        db.delete_unique('cookie_law_cookiebar', ['use_this', 'language'])

        # Deleting field 'CookieBar.title'
        db.delete_column('cookie_law_cookiebar', 'title')

        # Deleting field 'CookieBar.language'
        db.delete_column('cookie_law_cookiebar', 'language')

        # Adding unique constraint on 'CookieBar', fields ['use_this']
        db.create_unique('cookie_law_cookiebar', ['use_this'])

        # Changing field 'CookieBar.link_name'
        db.alter_column('cookie_law_cookiebar', 'link_name', self.gf('django.db.models.fields.CharField')(default=False, max_length=100))

        # Changing field 'CookieBar.link'
        db.alter_column('cookie_law_cookiebar', 'link', self.gf('django.db.models.fields.URLField')(default=u'http://www.wikipedia.org', max_length=255))


    models = {
        'cookie_law.cookiebar': {
            'Meta': {'unique_together': "(('use_this', 'language'),)", 'object_name': 'CookieBar'},
            'button_title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'link_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'use_this': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'cookie_law.cookieuser': {
            'Meta': {'object_name': 'CookieUser'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'agent': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['cookie_law']
