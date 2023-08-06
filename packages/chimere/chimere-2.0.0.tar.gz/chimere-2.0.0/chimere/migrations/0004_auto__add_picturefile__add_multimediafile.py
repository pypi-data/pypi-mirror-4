# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PictureFile'
        db.create_table('chimere_picturefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('miniature', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('chimere', ['PictureFile'])

        # Adding model 'MultimediaFile'
        db.create_table('chimere_multimediafile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('file_type', self.gf('django.db.models.fields.CharField')(max_length=6)),
        ))
        db.send_create_signal('chimere', ['MultimediaFile'])

        # Adding M2M table for field pictures on 'Marker'
        db.create_table('chimere_marker_pictures', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('marker', models.ForeignKey(orm['chimere.marker'], null=False)),
            (u'picturefile', models.ForeignKey(orm['chimere.picturefile'], null=False))
        ))
        db.create_unique('chimere_marker_pictures', ['marker_id', u'picturefile_id'])

        # Adding M2M table for field multimedia_files on 'Marker'
        db.create_table('chimere_marker_multimedia_files', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('marker', models.ForeignKey(orm['chimere.marker'], null=False)),
            (u'multimediafile', models.ForeignKey(orm['chimere.multimediafile'], null=False))
        ))
        db.create_unique('chimere_marker_multimedia_files', ['marker_id', u'multimediafile_id'])

        for marker in orm.Marker.objects.all():
            if marker.picture:
                picture = orm.PictureFile.objects.create(miniature=True,
                            picture=marker.picture, height=marker.height,
                            width=marker.width)
                marker.pictures.add(picture)
                marker.save()

    def backwards(self, orm):
        
        # Deleting model 'PictureFile'
        db.delete_table('chimere_picturefile')

        # Deleting model 'MultimediaFile'
        db.delete_table('chimere_multimediafile')

        # Removing M2M table for field pictures on 'Marker'
        db.delete_table('chimere_marker_pictures')

        # Removing M2M table for field multimedia_files on 'Marker'
        db.delete_table('chimere_marker_multimedia_files')


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
            'multimedia_files': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['chimere.MultimediaFile']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'pictures': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['chimere.PictureFile']", 'null': 'True', 'blank': 'True'}),
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
        'chimere.multimediafile': {
            'Meta': {'object_name': 'MultimediaFile'},
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'chimere.news': {
            'Meta': {'object_name': 'News'},
            'available': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'chimere.picturefile': {
            'Meta': {'object_name': 'PictureFile'},
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'miniature': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
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
