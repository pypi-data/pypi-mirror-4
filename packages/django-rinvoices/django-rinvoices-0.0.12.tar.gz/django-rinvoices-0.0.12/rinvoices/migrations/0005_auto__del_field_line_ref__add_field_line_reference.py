# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Line.ref'
        db.delete_column('rinvoices_line', 'ref')

        # Adding field 'Line.reference'
        db.add_column('rinvoices_line', 'reference',
                      self.gf('django.db.models.fields.CharField')(default=1, max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Line.ref'
        db.add_column('rinvoices_line', 'ref',
                      self.gf('django.db.models.fields.CharField')(default=1, max_length=200),
                      keep_default=False)

        # Deleting field 'Line.reference'
        db.delete_column('rinvoices_line', 'reference')


    models = {
        'rinvoices.currency': {
            'Meta': {'object_name': 'Currency'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'toeuro': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.header': {
            'Meta': {'object_name': 'Header'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'more': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rinvoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'currency'", 'to': "orm['rinvoices.Currency']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customer'", 'to': "orm['rinvoices.Customer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'header': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'header'", 'to': "orm['rinvoices.Header']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'invoice_number': ('django.db.models.fields.IntegerField', [], {}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'taxes': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taxes'", 'to': "orm['rinvoices.Tax']"})
        },
        'rinvoices.line': {
            'Meta': {'object_name': 'Line'},
            'amount': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'concept': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line'", 'to': "orm['rinvoices.Invoice']"}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit_price': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.tax': {
            'Meta': {'object_name': 'Tax'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['rinvoices']