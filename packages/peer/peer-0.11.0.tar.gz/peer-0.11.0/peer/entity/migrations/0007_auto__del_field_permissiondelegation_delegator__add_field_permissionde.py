# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'PermissionDelegation.delegator'
        db.delete_column('entity_permissiondelegation', 'delegator_id')

        # Adding field 'PermissionDelegation.delegate'
        db.add_column('entity_permissiondelegation', 'delegate', self.gf('django.db.models.fields.related.ForeignKey')(default=self.gf('django.contrib.auth.models.User').objects.get(username='admin').pk, related_name='permission_delegate', to=orm['auth.User']), keep_default=False)

        # Adding field 'PermissionDelegation.date'
        db.add_column('entity_permissiondelegation', 'date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now), keep_default=False)

        # Removing M2M table for field delegates on 'PermissionDelegation'
        db.delete_table('entity_permissiondelegation_delegates')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'PermissionDelegation.delegator'
        raise RuntimeError("Cannot reverse this migration. 'PermissionDelegation.delegator' and its values cannot be restored.")

        # Deleting field 'PermissionDelegation.delegate'
        db.delete_column('entity_permissiondelegation', 'delegate_id')

        # Deleting field 'PermissionDelegation.date'
        db.delete_column('entity_permissiondelegation', 'date')

        # Adding M2M table for field delegates on 'PermissionDelegation'
        db.create_table('entity_permissiondelegation_delegates', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permissiondelegation', models.ForeignKey(orm['entity.permissiondelegation'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('entity_permissiondelegation_delegates', ['permissiondelegation_id', 'user_id'])


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
        'domain.domain': {
            'Meta': {'object_name': 'Domain'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('peer.customfields.SafeCharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'validation_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'entity.entity': {
            'Meta': {'object_name': 'Entity'},
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'permission_delegated'", 'symmetrical': 'False', 'through': "orm['entity.PermissionDelegation']", 'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['domain.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('vff.field.VersionedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('peer.customfields.SafeCharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'entity.permissiondelegation': {
            'Meta': {'object_name': 'PermissionDelegation'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'delegate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'permission_delegate'", 'to': "orm['auth.User']"}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entity.Entity']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['entity']
