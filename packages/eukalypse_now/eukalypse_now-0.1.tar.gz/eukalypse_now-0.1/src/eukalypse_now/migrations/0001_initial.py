# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Project'
        db.create_table('eukalypse_now_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('eukalypse_now', ['Project'])

        # Adding model 'Test'
        db.create_table('eukalypse_now_test', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tests', to=orm['eukalypse_now.Project'])),
            ('identifier', self.gf('django.db.models.fields.SlugField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('eukalypse_now', ['Test'])

        # Adding model 'Testresult'
        db.create_table('eukalypse_now_testresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('test', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['eukalypse_now.Test'])),
            ('testrun', self.gf('django.db.models.fields.related.ForeignKey')(related_name='testresult', to=orm['eukalypse_now.Testrun'])),
            ('resultimage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('error', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('referenceimage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('errorimage', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('errorimage_improved', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('eukalypse_now', ['Testresult'])

        # Adding model 'Testrun'
        db.create_table('eukalypse_now_testrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='testrun', null=True, to=orm['eukalypse_now.Project'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('eukalypse_now', ['Testrun'])


    def backwards(self, orm):
        # Deleting model 'Project'
        db.delete_table('eukalypse_now_project')

        # Deleting model 'Test'
        db.delete_table('eukalypse_now_test')

        # Deleting model 'Testresult'
        db.delete_table('eukalypse_now_testresult')

        # Deleting model 'Testrun'
        db.delete_table('eukalypse_now_testrun')


    models = {
        'eukalypse_now.project': {
            'Meta': {'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'eukalypse_now.test': {
            'Meta': {'object_name': 'Test'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tests'", 'to': "orm['eukalypse_now.Project']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'eukalypse_now.testresult': {
            'Meta': {'object_name': 'Testresult'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'errorimage': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'errorimage_improved': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'referenceimage': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'resultimage': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'test': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['eukalypse_now.Test']"}),
            'testrun': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'testresult'", 'to': "orm['eukalypse_now.Testrun']"})
        },
        'eukalypse_now.testrun': {
            'Meta': {'object_name': 'Testrun'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'testrun'", 'null': 'True', 'to': "orm['eukalypse_now.Project']"})
        }
    }

    complete_apps = ['eukalypse_now']