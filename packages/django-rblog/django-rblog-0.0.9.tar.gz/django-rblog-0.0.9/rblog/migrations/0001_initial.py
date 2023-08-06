# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Post'
        db.create_table('rblog_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('hits', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='post_from', to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('thread_id', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
        ))
        db.send_create_signal('rblog', ['Post'])

        # Adding model 'Comments'
        db.create_table('rblog_comments', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('thread_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('thread_link', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('forum_id', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('author_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('author_email', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('author_url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('rblog', ['Comments'])


    def backwards(self, orm):
        # Deleting model 'Post'
        db.delete_table('rblog_post')

        # Deleting model 'Comments'
        db.delete_table('rblog_comments')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rblog.comments': {
            'Meta': {'object_name': 'Comments'},
            'author_email': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'author_url': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'comment_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'forum_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread_id': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'thread_link': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rblog.post': {
            'Meta': {'object_name': 'Post'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'thread_id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'post_from'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['rblog']