# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        db.rename_table('main_news', 'chimere_news')
        db.rename_table('main_tinyurl', 'chimere_tinyurl')
        db.rename_table('main_colortheme', 'chimere_colortheme')
        db.rename_table('main_color', 'chimere_color')
        db.rename_table('main_category', 'chimere_category')
        db.rename_table('main_icon', 'chimere_icon')
        db.rename_table('main_subcategory', 'chimere_subcategory')
        db.rename_table('main_marker', 'chimere_marker')
        db.rename_table('main_routefile', 'chimere_routefile')
        db.rename_table('main_route', 'chimere_route')
        db.rename_table('main_propertymodel', 'chimere_propertymodel')
        db.rename_table('main_property', 'chimere_property')
        db.rename_table('main_area', 'chimere_area')
        db.rename_table('main_marker_categories', 'chimere_marker_categories')
        db.rename_table('main_route_categories', 'chimere_route_categories')
        db.rename_table('main_subcategory_areas', 'chimere_subcategory_areas')

    def backwards(self, orm):
        db.rename_table('chimere_news', 'main_news')
        db.rename_table('chimere_tinyurl', 'main_tinyurl')
        db.rename_table('chimere_colortheme', 'main_colortheme')
        db.rename_table('chimere_color', '_color')
        db.rename_table('chimere_category', 'main_category')
        db.rename_table('chimere_icon', 'main_icon')
        db.rename_table('chimere_subcategory', 'main_subcategory')
        db.rename_table('chimere_marker', 'main_marker')
        db.rename_table('chimere_routefile', 'main_routefile')
        db.rename_table('chimere_route', 'main_route')
        db.rename_table('chimere_propertymodel', 'main_propertymodel')
        db.rename_table('chimere_property', 'main_property')
        db.rename_table('chimere_area', 'main_area')
        db.rename_table('chimere_marker_categories', 'main_marker_categories')
        db.rename_table('chimere_route_categories', 'main_route_categories')
        db.rename_table('chimere_subcategory_areas', 'main_subcategory_areas')
    
    models = {
        'chimere.area': {
            'Meta': {'object_name': 'Area'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lower_right_corner': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0 0)'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'upper_left_corner': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0 0)'"}),
            'urn': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '50', 'blank': 'True'})
        },
        'chimere.category': {
            'Meta': {'object_name': 'Category', 'db_table': "'main_category'"},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.color': {
            'Meta': {'object_name': 'Color', 'db_table': "'main_color'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'color_theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.ColorTheme']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.colortheme': {
            'Meta': {'object_name': 'ColorTheme', 'db_table': "'main_colortheme'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.icon': {
            'Meta': {'object_name': 'Icon', 'db_table': "'main_icon'"},
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.marker': {
            'Meta': {'object_name': 'Marker', 'db_table': "'main_marker'"},
            'available_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'point': ('chimere.widgets.PointField', [], {}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Route']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'chimere.news': {
            'Meta': {'object_name': 'News', 'db_table': "'main_news'"},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.property': {
            'Meta': {'object_name': 'Property', 'db_table': "'main_property'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Marker']"}),
            'propertymodel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.PropertyModel']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'chimere.propertymodel': {
            'Meta': {'object_name': 'PropertyModel', 'db_table': "'main_propertymodel'"},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'chimere.route': {
            'Meta': {'object_name': 'Route', 'db_table': "'main_route'"},
            'associated_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.RouteFile']", 'null': 'True', 'blank': 'True'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'route': ('chimere.widgets.RouteField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'chimere.routefile': {
            'Meta': {'object_name': 'RouteFile', 'db_table': "'main_routefile'"},
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'raw_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'simplified_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'chimere.subcategory': {
            'Meta': {'object_name': 'SubCategory', 'db_table': "'main_subcategory'"},
            'areas': ('chimere.widgets.SelectMultipleField', [], {'symmetrical': 'False', 'related_name': "'areas'", 'blank': 'True', 'to': "orm['chimere.Area']"}),
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Category']"}),
            'color_theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.ColorTheme']", 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Icon']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'chimere.tinyurl': {
            'Meta': {'object_name': 'TinyUrl', 'db_table': "'main_tinyurl'"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }
    
    complete_apps = ['chimere']
