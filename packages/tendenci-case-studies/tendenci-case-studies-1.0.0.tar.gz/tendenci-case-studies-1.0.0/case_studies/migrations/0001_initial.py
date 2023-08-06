# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'CaseStudy'
        db.create_table('case_studies_casestudy', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_user_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_view', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_user_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_member_edit', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('entity', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='case_studies_casestudy_entity', null=True, blank=True, to=orm['entities.Entity'])),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='case_studies_casestudy_creator', null=True, to=orm['auth.User'])),
            ('creator_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='case_studies_casestudy_owner', null=True, to=orm['auth.User'])),
            ('owner_username', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('status_detail', self.gf('django.db.models.fields.CharField')(default='active', max_length=50)),
            ('client', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=150)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('overview', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('execution', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('results', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('tags', self.gf('tagging.fields.TagField')()),
        ))
        db.send_create_signal('case_studies', ['CaseStudy'])

        # Adding M2M table for field services on 'CaseStudy'
        db.create_table('case_studies_casestudy_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('casestudy', models.ForeignKey(orm['case_studies.casestudy'], null=False)),
            ('service', models.ForeignKey(orm['case_studies.service'], null=False))
        ))
        db.create_unique('case_studies_casestudy_services', ['casestudy_id', 'service_id'])

        # Adding M2M table for field technologies on 'CaseStudy'
        db.create_table('case_studies_casestudy_technologies', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('casestudy', models.ForeignKey(orm['case_studies.casestudy'], null=False)),
            ('technology', models.ForeignKey(orm['case_studies.technology'], null=False))
        ))
        db.create_unique('case_studies_casestudy_technologies', ['casestudy_id', 'technology_id'])

        # Adding model 'Service'
        db.create_table('case_studies_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('case_studies', ['Service'])

        # Adding model 'Technology'
        db.create_table('case_studies_technology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('case_studies', ['Technology'])

        # Adding model 'Image'
        db.create_table('case_studies_image', (
            ('case_study', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['case_studies.CaseStudy'])),
            ('file_ptr', self.gf('django.db.models.fields.related.OneToOneField')(related_name='case_studies_image_related', unique=True, primary_key=True, to=orm['files.File'])),
            ('file_type', self.gf('django.db.models.fields.CharField')(default='other', max_length=50)),
            ('position', self.gf('django.db.models.fields.IntegerField')(blank=True)),
        ))
        db.send_create_signal('case_studies', ['Image'])


    def backwards(self, orm):
        
        # Deleting model 'CaseStudy'
        db.delete_table('case_studies_casestudy')

        # Removing M2M table for field services on 'CaseStudy'
        db.delete_table('case_studies_casestudy_services')

        # Removing M2M table for field technologies on 'CaseStudy'
        db.delete_table('case_studies_casestudy_technologies')

        # Deleting model 'Service'
        db.delete_table('case_studies_service')

        # Deleting model 'Technology'
        db.delete_table('case_studies_technology')

        # Deleting model 'Image'
        db.delete_table('case_studies_image')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 20, 12, 23, 15, 596425)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 20, 12, 23, 15, 596266)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'case_studies.casestudy': {
            'Meta': {'object_name': 'CaseStudy'},
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'client': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'case_studies_casestudy_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'case_studies_casestudy_entity'", 'null': 'True', 'blank': 'True', 'to': "orm['entities.Entity']"}),
            'execution': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overview': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'case_studies_casestudy_owner'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'results': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'services': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['case_studies.Service']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'technologies': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['case_studies.Technology']", 'symmetrical': 'False'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '150'})
        },
        'case_studies.image': {
            'Meta': {'ordering': "('position',)", 'object_name': 'Image', '_ormbases': ['files.File']},
            'case_study': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['case_studies.CaseStudy']"}),
            'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'case_studies_image_related'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['files.File']"}),
            'file_type': ('django.db.models.fields.CharField', [], {'default': "'other'", 'max_length': '50'}),
            'position': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'case_studies.service': {
            'Meta': {'ordering': "['title']", 'object_name': 'Service'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'case_studies.technology': {
            'Meta': {'ordering': "['title']", 'object_name': 'Technology'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'entities.entity': {
            'Meta': {'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity_parent_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        'files.file': {
            'Meta': {'object_name': 'File'},
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'files_file_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'files_file_entity'", 'null': 'True', 'blank': 'True', 'to': "orm['entities.Entity']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'files_file_owner'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {'null': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'perms.objectpermission': {
            'Meta': {'object_name': 'ObjectPermission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_groups.Group']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'user_groups.group': {
            'Meta': {'object_name': 'Group'},
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_self_add': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_self_remove': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_respond': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'auto_respond_priority': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'auto_respond_template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_groups_group_creator'", 'null': 'True', 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_recipient': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_groups_group_entity'", 'null': 'True', 'blank': 'True', 'to': "orm['entities.Entity']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['user_groups.GroupMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'user_groups_group_owner'", 'null': 'True', 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'group_permissions'", 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'show_as_option': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('tendenci.core.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'distribution'", 'max_length': '75', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'user_groups.groupmembership': {
            'Meta': {'unique_together': "(('group', 'member'),)", 'object_name': 'GroupMembership'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['user_groups.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_member'", 'to': "orm['auth.User']"}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['case_studies']
