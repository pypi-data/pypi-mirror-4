# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CookieBar'
        db.create_table('cookie_law_cookiebar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=255)),
            ('link_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('use_this', self.gf('django.db.models.fields.BooleanField')(default=False, unique=True)),
        ))
        db.send_create_signal('cookie_law', ['CookieBar'])


    def backwards(self, orm):
        
        # Deleting model 'CookieBar'
        db.delete_table('cookie_law_cookiebar')


    models = {
        'cookie_law.cookiebar': {
            'Meta': {'object_name': 'CookieBar'},
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
