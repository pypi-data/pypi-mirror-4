# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Currency'
        db.create_table('rinvoices_currency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('toeuro', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('rinvoices', ['Currency'])

        # Adding model 'Tax'
        db.create_table('rinvoices_tax', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('rinvoices', ['Tax'])

        # Adding field 'Invoice.registered'
        db.add_column('rinvoices_invoice', 'registered',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Invoice.taxes'
        db.add_column('rinvoices_invoice', 'taxes',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='taxes', to=orm['rinvoices.Tax']),
                      keep_default=False)

        # Adding field 'Invoice.currency'
        db.add_column('rinvoices_invoice', 'currency',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='currency', to=orm['rinvoices.Currency']),
                      keep_default=False)

        # Adding field 'Invoice.date'
        db.add_column('rinvoices_invoice', 'date',
                      self.gf('django.db.models.fields.DateTimeField')(default='2012-11-11 12:12:12'),
                      keep_default=False)

        # Adding field 'Invoice.image'
        db.add_column('rinvoices_invoice', 'image',
                      self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100, blank=True),
                      keep_default=False)

        # Adding field 'Invoice.invoice_number'
        db.add_column('rinvoices_invoice', 'invoice_number',
                      self.gf('django.db.models.fields.IntegerField')(default='1'),
                      keep_default=False)


        # Changing field 'Header.email'
        db.alter_column('rinvoices_header', 'email', self.gf('django.db.models.fields.EmailField')(max_length=100))

    def backwards(self, orm):
        # Deleting model 'Currency'
        db.delete_table('rinvoices_currency')

        # Deleting model 'Tax'
        db.delete_table('rinvoices_tax')

        # Deleting field 'Invoice.registered'
        db.delete_column('rinvoices_invoice', 'registered')

        # Deleting field 'Invoice.taxes'
        db.delete_column('rinvoices_invoice', 'taxes_id')

        # Deleting field 'Invoice.currency'
        db.delete_column('rinvoices_invoice', 'currency_id')

        # Deleting field 'Invoice.date'
        db.delete_column('rinvoices_invoice', 'date')

        # Deleting field 'Invoice.image'
        db.delete_column('rinvoices_invoice', 'image')

        # Deleting field 'Invoice.invoice_number'
        db.delete_column('rinvoices_invoice', 'invoice_number')


        # Changing field 'Header.email'
        db.alter_column('rinvoices_header', 'email', self.gf('django.db.models.fields.CharField')(max_length=100))

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
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
