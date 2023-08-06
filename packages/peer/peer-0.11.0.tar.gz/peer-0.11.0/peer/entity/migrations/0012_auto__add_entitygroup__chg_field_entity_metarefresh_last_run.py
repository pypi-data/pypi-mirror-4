# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EntityGroup'
        db.create_table('entity_entitygroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('peer.customfields.SafeCharField')(max_length=200)),
            ('query', self.gf('peer.customfields.SafeCharField')(max_length=100)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('entity', ['EntityGroup'])

        # Changing field 'Entity.metarefresh_last_run'
        db.alter_column('entity_entity', 'metarefresh_last_run', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Adding index on 'Entity', fields ['metarefresh_frequency']
        db.create_index('entity_entity', ['metarefresh_frequency'])


    def backwards(self, orm):
        
        # Removing index on 'Entity', fields ['metarefresh_frequency']
        db.delete_index('entity_entity', ['metarefresh_frequency'])

        # Deleting model 'EntityGroup'
        db.delete_table('entity_entitygroup')

        # Changing field 'Entity.metarefresh_last_run'
        db.alter_column('entity_entity', 'metarefresh_last_run', self.gf('django.db.models.fields.DateTimeField')())


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
            'team': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'team_domains'", 'symmetrical': 'False', 'through': "orm['domain.DomainTeamMembership']", 'to': "orm['auth.User']"}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'validation_key': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'domain.domainteammembership': {
            'Meta': {'object_name': 'DomainTeamMembership'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['domain.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'domain_teams'", 'to': "orm['auth.User']"})
        },
        'entity.entity': {
            'Meta': {'ordering': "('-creation_time',)", 'object_name': 'Entity'},
            'creation_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'delegates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'permission_delegated'", 'symmetrical': 'False', 'through': "orm['entity.PermissionDelegation']", 'to': "orm['auth.User']"}),
            'domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['domain.Domain']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('vff.field.VersionedFileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'metarefresh_frequency': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '1', 'db_index': 'True'}),
            'metarefresh_last_run': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'modification_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('peer.customfields.SafeCharField', [], {'max_length': '100'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'entity.entitygroup': {
            'Meta': {'object_name': 'EntityGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('peer.customfields.SafeCharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'query': ('peer.customfields.SafeCharField', [], {'max_length': '100'})
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
