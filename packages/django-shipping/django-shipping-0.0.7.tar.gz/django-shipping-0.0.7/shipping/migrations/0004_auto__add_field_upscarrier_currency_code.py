# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UPSCarrier.currency_code'
        db.add_column('shipping_upscarrier', 'currency_code',
                      self.gf('django.db.models.fields.CharField')(default='USD', max_length=3),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UPSCarrier.currency_code'
        db.delete_column('shipping_upscarrier', 'currency_code')


    models = {
        'shipping.bin': {
            'Meta': {'object_name': 'Bin'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bins'", 'to': "orm['shipping.Carrier']"}),
            'height': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'weight': ('django.db.models.fields.FloatField', [], {}),
            'width': ('django.db.models.fields.FloatField', [], {})
        },
        'shipping.carrier': {
            'Meta': {'object_name': 'Carrier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'max_length': '2'})
        },
        'shipping.correioscarrier': {
            'Meta': {'object_name': 'CorreiosCarrier', '_ormbases': ['shipping.Carrier']},
            'carrier_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['shipping.Carrier']", 'unique': 'True', 'primary_key': 'True'}),
            'correios_company': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'correios_password': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'shipping.country': {
            'Meta': {'object_name': 'Country'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'zone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shipping.Zone']"})
        },
        'shipping.state': {
            'Meta': {'object_name': 'State'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'states'", 'null': 'True', 'to': "orm['shipping.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'shipping.upscarrier': {
            'Meta': {'object_name': 'UPSCarrier', '_ormbases': ['shipping.Carrier']},
            'address_line_1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'address_line_2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'carrier_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['shipping.Carrier']", 'unique': 'True', 'primary_key': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shipping.Country']", 'null': 'True'}),
            'currency_code': ('django.db.models.fields.CharField', [], {'default': "'USD'", 'max_length': '3'}),
            'dimension_unit': ('django.db.models.fields.CharField', [], {'default': "'CM'", 'max_length': '3'}),
            'package_type': ('django.db.models.fields.CharField', [], {'default': "'21'", 'max_length': '3'}),
            'pickup_type': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True'}),
            'rate_service': ('django.db.models.fields.IntegerField', [], {'default': '8', 'max_length': '2'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shipping.State']", 'null': 'True'}),
            'ups_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'ups_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'ups_login': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'ups_password': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'weight_unit': ('django.db.models.fields.CharField', [], {'default': "'KGS'", 'max_length': '3'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'})
        },
        'shipping.zone': {
            'Meta': {'object_name': 'Zone'},
            'carrier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shipping.Carrier']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.IntegerField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['shipping']