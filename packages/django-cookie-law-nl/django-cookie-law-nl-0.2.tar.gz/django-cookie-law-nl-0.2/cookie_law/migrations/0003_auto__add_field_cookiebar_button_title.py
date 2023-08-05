# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CookieBar.button_title'
        db.add_column('cookie_law_cookiebar', 'button_title', self.gf('django.db.models.fields.CharField')(default='Allow Cookies', max_length=50), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CookieBar.button_title'
        db.delete_column('cookie_law_cookiebar', 'button_title')


    models = {
        'cookie_law.cookiebar': {
            'Meta': {'object_name': 'CookieBar'},
            'button_title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '255'}),
            'link_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'use_this': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'unique': 'True'})
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
