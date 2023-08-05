# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Testresult.errorstate'
        db.delete_column('eukalypse_now_testresult', 'errorstate')

        # Adding field 'Testresult.error_acknowledged'
        db.add_column('eukalypse_now_testresult', 'error_acknowledged',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Testresult.error_reference_updated'
        db.add_column('eukalypse_now_testresult', 'error_reference_updated',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Testresult.errorstate'
        db.add_column('eukalypse_now_testresult', 'errorstate',
                      self.gf('django.db.models.fields.CharField')(default='default', max_length=20),
                      keep_default=False)

        # Deleting field 'Testresult.error_acknowledged'
        db.delete_column('eukalypse_now_testresult', 'error_acknowledged')

        # Deleting field 'Testresult.error_reference_updated'
        db.delete_column('eukalypse_now_testresult', 'error_reference_updated')


    models = {
        'eukalypse_now.project': {
            'Meta': {'object_name': 'Project'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'notify_mail': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_only_error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'notify_recipient': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'eukalypse_now.test': {
            'Meta': {'object_name': 'Test'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.SlugField', [], {'max_length': '200'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tests'", 'to': "orm['eukalypse_now.Project']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'wait': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'eukalypse_now.testresult': {
            'Meta': {'object_name': 'Testresult'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'error_acknowledged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'error_reference_updated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'testrun'", 'null': 'True', 'to': "orm['eukalypse_now.Project']"})
        }
    }

    complete_apps = ['eukalypse_now']