# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Token'
        db.create_table('oauth_token', (
            ('consumer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oauth_backend.Consumer'])),
            ('token', self.gf('django.db.models.fields.CharField')(default='pTgxDvhGsCicVEXkoshpryVOaQFuVrsiOxvvhxGGQWksaCVDUf', max_length=50, primary_key=True)),
            ('token_secret', self.gf('django.db.models.fields.CharField')(default='IAxghXCOSvAiXfiFAXHSOAvJyiGjSMWgJmjqKqMvRHBqeIDZxS', max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.utcnow)),
        ))
        db.send_create_signal('oauth_backend', ['Token'])

        # Adding model 'Consumer'
        db.create_table('oauth_consumer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='oauth_consumer', unique=True, to=orm['auth.User'])),
            ('secret', self.gf('django.db.models.fields.CharField')(default='yhHOhStulrOConzqoEbdZAqGRnqDqO', max_length=255, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('oauth_backend', ['Consumer'])

        # Adding model 'Nonce'
        db.create_table('oauth_nonce', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oauth_backend.Token'])),
            ('consumer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oauth_backend.Consumer'])),
            ('nonce', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('oauth_backend', ['Nonce'])


    def backwards(self, orm):
        # Deleting model 'Token'
        db.delete_table('oauth_token')

        # Deleting model 'Consumer'
        db.delete_table('oauth_consumer')

        # Deleting model 'Nonce'
        db.delete_table('oauth_nonce')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'oauth_backend.consumer': {
            'Meta': {'object_name': 'Consumer', 'db_table': "'oauth_consumer'"},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'default': "'UuqZUYLiWrCOLdHPduEUcBRMuVtCQN'", 'max_length': '255', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'oauth_consumer'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'oauth_backend.nonce': {
            'Meta': {'object_name': 'Nonce', 'db_table': "'oauth_nonce'"},
            'consumer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oauth_backend.Consumer']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nonce': ('django.db.models.fields.CharField', [], {'max_length': '255', 'unique': 'True'}),
            'token': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oauth_backend.Token']"})
        },
        'oauth_backend.token': {
            'Meta': {'object_name': 'Token', 'db_table': "'oauth_token'"},
            'consumer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oauth_backend.Consumer']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'QHCoAVrJpzOuUBVtXObPwKSInluNaTDxHrqFjTzTebyvqMJSXm'", 'max_length': '50', 'primary_key': 'True'}),
            'token_secret': ('django.db.models.fields.CharField', [], {'default': "'geJdlQXnIAsvHigtpThlcbWWxhrPZQlKPNIgngeYksvuElYhbc'", 'max_length': '50'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow'})
        }
    }

    complete_apps = ['oauth_backend']