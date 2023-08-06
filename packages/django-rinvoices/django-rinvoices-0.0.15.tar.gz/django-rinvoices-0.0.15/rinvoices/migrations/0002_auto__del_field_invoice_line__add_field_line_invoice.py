# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Invoice.line'
        db.delete_column('rinvoices_invoice', 'line_id')

        # Adding field 'Line.invoice'
        db.add_column('rinvoices_line', 'invoice',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='line', to=orm['rinvoices.Header']),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Invoice.line'
        db.add_column('rinvoices_invoice', 'line',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='lineinvoice', to=orm['rinvoices.Line']),
                      keep_default=False)

        # Deleting field 'Line.invoice'
        db.delete_column('rinvoices_line', 'invoice_id')


    models = {
        'rinvoices.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.header': {
            'Meta': {'object_name': 'Header'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'more': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rinvoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customerinvoice'", 'to': "orm['rinvoices.Customer']"}),
            'header': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'headerinvoice'", 'to': "orm['rinvoices.Header']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'rinvoices.line': {
            'Meta': {'object_name': 'Line'},
            'amount': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'concept': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line'", 'to': "orm['rinvoices.Header']"}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit_price': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['rinvoices']