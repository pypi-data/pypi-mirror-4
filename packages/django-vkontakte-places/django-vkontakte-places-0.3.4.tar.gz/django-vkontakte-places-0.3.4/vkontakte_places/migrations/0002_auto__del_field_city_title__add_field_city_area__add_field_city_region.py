# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'City.title'
        db.delete_column('vkontakte_places_city', 'title')

        # Adding field 'City.area'
        db.add_column('vkontakte_places_city', 'area', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Adding field 'City.region'
        db.add_column('vkontakte_places_city', 'region', self.gf('django.db.models.fields.CharField')(default='', max_length=100), keep_default=False)

        # Deleting field 'Region.title'
        db.delete_column('vkontakte_places_region', 'title')

        # Deleting field 'Country.title'
        db.delete_column('vkontakte_places_country', 'title')


    def backwards(self, orm):
        
        # Adding field 'City.title'
        db.add_column('vkontakte_places_city', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=50), keep_default=False)

        # Deleting field 'City.area'
        db.delete_column('vkontakte_places_city', 'area')

        # Deleting field 'City.region'
        db.delete_column('vkontakte_places_city', 'region')

        # Adding field 'Region.title'
        db.add_column('vkontakte_places_region', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=50), keep_default=False)

        # Adding field 'Country.title'
        db.add_column('vkontakte_places_country', 'title', self.gf('django.db.models.fields.CharField')(default='', max_length=50), keep_default=False)


    models = {
        'vkontakte_places.city': {
            'Meta': {'ordering': "['name']", 'object_name': 'City'},
            'area': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cities'", 'null': 'True', 'to': "orm['vkontakte_places.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        },
        'vkontakte_places.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        },
        'vkontakte_places.region': {
            'Meta': {'ordering': "['name']", 'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'regions'", 'to': "orm['vkontakte_places.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'remote_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['vkontakte_places']
