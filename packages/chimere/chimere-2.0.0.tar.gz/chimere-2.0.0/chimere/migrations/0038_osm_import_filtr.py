# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for importer in orm['chimere.Importer'].objects.filter(
                                           importer_type='OSM').all():
            if importer.filtr:
                continue
            splited_url = importer.source.split('/')
            importer.filtr = splited_url[-1]
            importer.source = "/".join(splited_url[:-1])+"/"
            importer.save()

    def backwards(self, orm):
        # no backward necessary
        pass

    models = {
        'chimere.area': {
            'Meta': {'ordering': "('order', 'name')", 'object_name': 'Area'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'default_subcategories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False', 'blank': 'True'}),
            'dynamic_categories': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'external_css': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layers': ('chimere.widgets.SelectMultipleField', [], {'symmetrical': 'False', 'related_name': "'areas'", 'blank': 'True', 'through': "orm['chimere.AreaLayers']", 'to': "orm['chimere.Layer']"}),
            'lower_right_corner': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0 0)'"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'restrict_to_extent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subcategories': ('chimere.widgets.SelectMultipleField', [], {'symmetrical': 'False', 'related_name': "'areas'", 'blank': 'True', 'db_table': "'chimere_subcategory_areas'", 'to': "orm['chimere.SubCategory']"}),
            'upper_left_corner': ('django.contrib.gis.db.models.fields.PointField', [], {'default': "'POINT(0 0)'"}),
            'urn': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'welcome_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'chimere.arealayers': {
            'Meta': {'ordering': "('order',)", 'object_name': 'AreaLayers'},
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Area']"}),
            'default': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Layer']"}),
            'order': ('django.db.models.fields.IntegerField', [], {})
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
        'chimere.importer': {
            'Meta': {'object_name': 'Importer'},
            'associate_marker_to_way': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'default_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'filtr': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importer_type': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'source_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'srid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'zipped': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'chimere.layer': {
            'Meta': {'object_name': 'Layer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layer_code': ('django.db.models.fields.TextField', [], {'max_length': '300'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.marker': {
            'Meta': {'ordering': "('status', 'name')", 'object_name': 'Marker'},
            'available_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'import_source': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'import_version': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified_since_import': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'not_for_osm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'point': ('chimere.widgets.PointField', [], {}),
            'ref_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submited_marker'", 'null': 'True', 'to': "orm['chimere.Marker']"}),
            'route': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'associated_marker'", 'null': 'True', 'to': "orm['chimere.Route']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submiter_comment': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'submiter_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'submiter_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'submiter_session_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'})
        },
        'chimere.multimediafile': {
            'Meta': {'object_name': 'MultimediaFile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'multimedia_files'", 'to': "orm['chimere.Marker']"}),
            'miniature': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'multimedia_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.MultimediaType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'chimere.multimediatype': {
            'Meta': {'object_name': 'MultimediaType'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iframe': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.news': {
            'Meta': {'object_name': 'News'},
            'areas': ('chimere.widgets.SelectMultipleField', [], {'symmetrical': 'False', 'to': "orm['chimere.Area']", 'null': 'True', 'blank': 'True'}),
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.picturefile': {
            'Meta': {'object_name': 'PictureFile'},
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pictures'", 'to': "orm['chimere.Marker']"}),
            'miniature': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'thumbnailfile': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'thumbnailfile_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'thumbnailfile_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
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
            'mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'subcategories': ('chimere.widgets.SelectMultipleField', [], {'symmetrical': 'False', 'related_name': "'properties'", 'blank': 'True', 'to': "orm['chimere.SubCategory']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'chimere.route': {
            'Meta': {'ordering': "('status', 'name')", 'object_name': 'Route'},
            'associated_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.RouteFile']", 'null': 'True', 'blank': 'True'}),
            'categories': ('chimere.widgets.SelectMultipleField', [], {'to': "orm['chimere.SubCategory']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'has_associated_marker': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'import_key': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'import_source': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'import_version': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'modified_since_import': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'not_for_osm': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ref_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submited_route'", 'null': 'True', 'to': "orm['chimere.Route']"}),
            'route': ('chimere.widgets.RouteField', [], {}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'submiter_comment': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'submiter_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'submiter_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
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
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subcategories'", 'to': "orm['chimere.Category']"}),
            'color_theme': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.ColorTheme']", 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['chimere.Icon']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'submission': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'chimere.tinyurl': {
            'Meta': {'object_name': 'TinyUrl'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['chimere']
    symmetrical = True
