# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Route.submiter_session_key'
        db.add_column('chimere_route', 'submiter_session_key', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True), keep_default=False)

        # Adding field 'Route.submiter_email'
        db.add_column('chimere_route', 'submiter_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)

        # Adding field 'Route.submiter_comment'
        db.add_column('chimere_route', 'submiter_comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Route.ref_item'
        db.add_column('chimere_route', 'ref_item', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='submited_route', null=True, to=orm['chimere.Route']), keep_default=False)

        # Adding field 'Marker.submiter_session_key'
        db.add_column('chimere_marker', 'submiter_session_key', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True), keep_default=False)

        # Adding field 'Marker.submiter_email'
        db.add_column('chimere_marker', 'submiter_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True), keep_default=False)

        # Adding field 'Marker.submiter_comment'
        db.add_column('chimere_marker', 'submiter_comment', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True), keep_default=False)

        # Adding field 'Marker.ref_item'
        db.add_column('chimere_marker', 'ref_item', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='submited_marker', null=True, to=orm['chimere.Marker']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Route.submiter_session_key'
        db.delete_column('chimere_route', 'submiter_session_key')

        # Deleting field 'Route.submiter_email'
        db.delete_column('chimere_route', 'submiter_email')

        # Deleting field 'Route.submiter_comment'
        db.delete_column('chimere_route', 'submiter_comment')

        # Deleting field 'Route.ref_item'
        db.delete_column('chimere_route', 'ref_item_id')

        # Deleting field 'Marker.submiter_session_key'
        db.delete_column('chimere_marker', 'submiter_session_key')

        # Deleting field 'Marker.submiter_email'
        db.delete_column('chimere_marker', 'submiter_email')

        # Deleting field 'Marker.submiter_comment'
        db.delete_column('chimere_marker', 'submiter_comment')

        # Deleting field 'Marker.ref_item'
        db.delete_column('chimere_marker', 'ref_item_id')


    models = {
        'chimere.area': {
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Area'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lower_right_corner': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0 0)'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'upper_left_corner': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0 0)'"}),
            'urn': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'chimere.category': {
            'Meta': {'ordering': "['order']", 'object_name': 'Category'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.color': {
            'Meta': {'ordering': "['order']", 'object_name': 'Color'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'color_theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.ColorTheme']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.colortheme': {
            'Meta': {'object_name': 'ColorTheme'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.icon': {
            'Meta': {'object_name': 'Icon'},
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.marker': {
            'Meta': {'ordering': "('status', 'name')", 'object_name': 'Marker'},
            'available_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'point': ('chimere.widgets.PointField', [], {}),
            'ref_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submited_marker'", 'null': 'True', 'to': "orm['chimere.Marker']"}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'associated_marker'", 'null': 'True', 'to': "orm['chimere.Route']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submiter_comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'submiter_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'submiter_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'chimere.news': {
            'Meta': {'object_name': 'News'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.property': {
            'Meta': {'object_name': 'Property'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Marker']"}),
            'propertymodel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.PropertyModel']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'chimere.propertymodel': {
            'Meta': {'ordering': "('order',)", 'object_name': 'PropertyModel'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'chimere.route': {
            'Meta': {'ordering': "('status', 'name')", 'object_name': 'Route'},
            'associated_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.RouteFile']", 'null': 'True', 'blank': 'True'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ref_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submited_route'", 'null': 'True', 'to': "orm['chimere.Route']"}),
            'route': ('chimere.widgets.RouteField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submiter_comment': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'submiter_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'submiter_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'chimere.routefile': {
            'Meta': {'ordering': "('name',)", 'object_name': 'RouteFile'},
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'raw_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'simplified_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'chimere.subcategory': {
            'Meta': {'ordering': "['category', 'order']", 'object_name': 'SubCategory'},
            'areas': ('chimere.widgets.SelectMultipleField', [], {'symmetrical': 'False', 'related_name': "'areas'", 'blank': 'True', 'to': "orm['chimere.Area']"}),
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Category']"}),
            'color_theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.ColorTheme']", 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Icon']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.tinyurl': {
            'Meta': {'object_name': 'TinyUrl'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['chimere']
