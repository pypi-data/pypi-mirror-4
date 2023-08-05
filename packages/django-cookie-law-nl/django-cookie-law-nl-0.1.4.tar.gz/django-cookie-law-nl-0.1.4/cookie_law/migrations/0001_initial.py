# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CookieUser'
        db.create_table('cookie_law_cookieuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=39)),
            ('agent', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('cookie_law', ['CookieUser'])


    def backwards(self, orm):
        
        # Deleting model 'CookieUser'
        db.delete_table('cookie_law_cookieuser')


    models = {
        'cookie_law.cookieuser': {
            'Meta': {'object_name': 'CookieUser'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '39'}),
            'agent': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['cookie_law']
