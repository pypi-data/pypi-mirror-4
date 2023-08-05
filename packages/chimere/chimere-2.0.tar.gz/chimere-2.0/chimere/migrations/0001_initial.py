# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'News'
        db.create_table('main_news', (
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('chimere', ['News'])

        # Adding model 'TinyUrl'
        db.create_table('main_tinyurl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parameters', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('chimere', ['TinyUrl'])

        # Adding model 'ColorTheme'
        db.create_table('main_colortheme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('chimere', ['ColorTheme'])

        # Adding model 'Color'
        db.create_table('main_color', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('color_theme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.ColorTheme'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('chimere', ['Color'])

        # Adding model 'Category'
        db.create_table('main_category', (
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('chimere', ['Category'])

        # Adding model 'Icon'
        db.create_table('main_icon', (
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('chimere', ['Icon'])

        # Adding model 'SubCategory'
        db.create_table('main_subcategory', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.Category'])),
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('item_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('color_theme', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.ColorTheme'], null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('icon', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.Icon'])),
        ))
        db.send_create_signal('chimere', ['SubCategory'])

        # Adding M2M table for field areas on 'SubCategory'
        db.create_table('main_subcategory_areas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('subcategory', models.ForeignKey(orm['chimere.subcategory'], null=False)),
            ('area', models.ForeignKey(orm['chimere.area'], null=False))
        ))
        db.create_unique('main_subcategory_areas', ['subcategory_id', 'area_id'])

        # Adding model 'Marker'
        db.create_table('main_marker', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('point', self.gf('chimere.widgets.PointField')()),
            ('route', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.Route'], null=True, blank=True)),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('available_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('chimere', ['Marker'])

        # Adding M2M table for field categories on 'Marker'
        db.create_table('main_marker_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('marker', models.ForeignKey(orm['chimere.marker'], null=False)),
            ('subcategory', models.ForeignKey(orm['chimere.subcategory'], null=False))
        ))
        db.create_unique('main_marker_categories', ['marker_id', 'subcategory_id'])

        # Adding model 'RouteFile'
        db.create_table('main_routefile', (
            ('file_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('raw_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('simplified_file', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('chimere', ['RouteFile'])

        # Adding model 'Route'
        db.create_table('main_route', (
            ('status', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('route', self.gf('chimere.widgets.RouteField')()),
            ('height', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('width', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('associated_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.RouteFile'], null=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('chimere', ['Route'])

        # Adding M2M table for field categories on 'Route'
        db.create_table('main_route_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('route', models.ForeignKey(orm['chimere.route'], null=False)),
            ('subcategory', models.ForeignKey(orm['chimere.subcategory'], null=False))
        ))
        db.create_unique('main_route_categories', ['route_id', 'subcategory_id'])

        # Adding model 'Area'
        db.create_table('main_area', (
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('urn', self.gf('django.db.models.fields.SlugField')(db_index=True, unique=True, max_length=50, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('upper_left_corner', self.gf('django.contrib.gis.db.models.fields.PointField')(default='POINT(0 0)')),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('lower_right_corner', self.gf('django.contrib.gis.db.models.fields.PointField')(default='POINT(0 0)')),
        ))
        db.send_create_signal('chimere', ['Area'])

        # Adding model 'PropertyModel'
        db.create_table('main_propertymodel', (
            ('available', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('chimere', ['PropertyModel'])

        # Adding model 'Property'
        db.create_table('main_property', (
            ('marker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.Marker'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('propertymodel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['chimere.PropertyModel'])),
        ))
        db.send_create_signal('chimere', ['Property'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'News'
        db.delete_table('main_news')

        # Deleting model 'TinyUrl'
        db.delete_table('main_tinyurl')

        # Deleting model 'ColorTheme'
        db.delete_table('main_colortheme')

        # Deleting model 'Color'
        db.delete_table('main_color')

        # Deleting model 'Category'
        db.delete_table('main_category')

        # Deleting model 'Icon'
        db.delete_table('main_icon')

        # Deleting model 'SubCategory'
        db.delete_table('main_subcategory')

        # Removing M2M table for field areas on 'SubCategory'
        db.delete_table('main_subcategory_areas')

        # Deleting model 'Marker'
        db.delete_table('main_marker')

        # Removing M2M table for field categories on 'Marker'
        db.delete_table('main_marker_categories')

        # Deleting model 'RouteFile'
        db.delete_table('main_routefile')

        # Deleting model 'Route'
        db.delete_table('main_route')

        # Removing M2M table for field categories on 'Route'
        db.delete_table('main_route_categories')

        # Deleting model 'Area'
        db.delete_table('main_area')

        # Deleting model 'PropertyModel'
        db.delete_table('main_propertymodel')

        # Deleting model 'Property'
        db.delete_table('main_property')
    
    
    models = {
        'chimere.area': {
            'Meta': {'object_name': 'Area', 'db_table': "'main_area'"},
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
