# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Header'
        db.create_table('rinvoices_header', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('cif', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('more', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('rinvoices', ['Header'])

        # Adding model 'Customer'
        db.create_table('rinvoices_customer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('cif', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('rinvoices', ['Customer'])

        # Adding model 'Line'
        db.create_table('rinvoices_line', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('concept', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('quantity', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('unit_price', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('amount', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('rinvoices', ['Line'])

        # Adding model 'Invoice'
        db.create_table('rinvoices_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('header', self.gf('django.db.models.fields.related.ForeignKey')(related_name='headerinvoice', to=orm['rinvoices.Header'])),
            ('line', self.gf('django.db.models.fields.related.ForeignKey')(related_name='lineinvoice', to=orm['rinvoices.Line'])),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='customerinvoice', to=orm['rinvoices.Customer'])),
        ))
        db.send_create_signal('rinvoices', ['Invoice'])


    def backwards(self, orm):
        # Deleting model 'Header'
        db.delete_table('rinvoices_header')

        # Deleting model 'Customer'
        db.delete_table('rinvoices_customer')

        # Deleting model 'Line'
        db.delete_table('rinvoices_line')

        # Deleting model 'Invoice'
        db.delete_table('rinvoices_invoice')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'lineinvoice'", 'to': "orm['rinvoices.Line']"})
        },
        'rinvoices.line': {
            'Meta': {'object_name': 'Line'},
            'amount': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'concept': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit_price': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['rinvoices']