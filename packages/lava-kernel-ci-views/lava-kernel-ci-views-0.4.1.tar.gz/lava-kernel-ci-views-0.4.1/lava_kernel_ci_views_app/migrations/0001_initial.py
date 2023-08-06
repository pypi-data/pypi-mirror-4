# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BoardType'
        db.create_table('lava_kernel_ci_views_app_boardtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.TextField')()),
            ('icon', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('lava_kernel_ci_views_app', ['BoardType'])


    def backwards(self, orm):
        
        # Deleting model 'BoardType'
        db.delete_table('lava_kernel_ci_views_app_boardtype')


    models = {
        'lava_kernel_ci_views_app.boardtype': {
            'Meta': {'object_name': 'BoardType'},
            'display_name': ('django.db.models.fields.TextField', [], {}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['lava_kernel_ci_views_app']
