# -*- coding: utf-8 -*-

"""
Models for the "flatpages" project
"""

import time
import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.conf import settings as conf

class Header(models.Model):
    """
    Header invoice model
    """
    name = models.CharField(_('Name'), max_length=200)
    address = models.CharField(_('Address'), max_length=200)
    city = models.CharField(_('City'), max_length=100)
    country = models.CharField(_('Country'), max_length=100)
    email = models.EmailField(_('Email'), blank=True, max_length=100)
    phone = models.CharField(_('Phone'), max_length=100)
    cif = models.CharField(_('CIF/NIF'), max_length=100)
    more = models.TextField(_('Extra information'), blank=True)

    def __unicode__(self):
        return self.name + ' ' + self.address

    class Meta:
        verbose_name = _('Header')
        verbose_name_plural = _('Headers')


class Customer(models.Model):
    """
    Customers model
    """
    name = models.CharField(_('Customer'), max_length=200)
    address = models.CharField(_('Address'), max_length=200)
    cif = models.CharField(_('CIF/NIF'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')


class Provider(models.Model):
    """
    Customers model
    """
    name = models.CharField(_('Customer'), max_length=200)
    address = models.CharField(_('Address'), max_length=200)
    cif = models.CharField(_('CIF/NIF'), max_length=100, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')


class Currency(models.Model):
    """
    Customers model
    """
    name = models.CharField(_('Currency'), max_length=200)
    symbol = models.CharField(_('Symbol'), max_length=200)
    toeuro = models.CharField(_('Change to EUR'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

class Tax(models.Model):
    """
    Customers model
    """
    name = models.CharField(_('Tax'), max_length=200)
    value = models.CharField(_('Value'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Tax')
        verbose_name_plural = _('Taxes')


class Retention(models.Model):
    """
    Customers model
    """
    name = models.CharField(_('Tax'), max_length=200)
    value = models.CharField(_('Value'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Retention')
        verbose_name_plural = _('Retentions')


class QuantityUnit(models.Model):
    """
    Customers model
    """
    name = models.CharField(_('Quantity Unit'), max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('QuantityUnit')
        verbose_name_plural = _('QuantityUnits')


class Invoice(models.Model):
    """
    Invoice model
    """
    header = models.ForeignKey(Header, related_name="header")
    customer = models.ForeignKey(Customer, related_name="customer")
    registered = models.BooleanField(_("Registered"), help_text=_('Registered yet?'))
    sent = models.BooleanField(_("Sent"), help_text=_('Invoice sent?'))
    charged = models.BooleanField(_("Charged"), help_text=_('Invoice charged?'))
    taxes = models.ForeignKey(Tax, related_name="taxes")
    retentions = models.ForeignKey(Retention, related_name="retentions", default='', blank=True)
    currency = models.ForeignKey(Currency, related_name="currency")
    date = models.DateTimeField(_('Creation date'))
    invoice_number = models.IntegerField(_('Invoice Number'))
    subtotal = models.CharField(_('Subtotal'), blank=True, max_length=200, help_text=_('Calculated field'))
    subtotal_iva = models.CharField(_('Subtotal IVA'), blank=True, max_length=200, help_text=_('Calculated field'))
    subtotal_retentions = models.CharField(_('Subtotal Retentions'), blank=True, max_length=200, help_text=_('Calculated field'))
    total = models.CharField(_('Total'), max_length=200, blank=True, help_text=_('Calculated field'))

    def __unicode__(self):
        return str(self.invoice_number) + "->" + str(self.date)

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

class InvoiceReceive(models.Model):
    """
    Receive Invoices model
    """
    provider = models.ForeignKey(Provider, related_name="provider", blank=True, default='')
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    registered = models.BooleanField(_("Registered"), help_text=_('Registered yet?'))
    file = models.FileField(_('File, Image, PDF'), upload_to='media/invoices', blank=True)
    reference = models.CharField(_('Reference'), max_length=200, blank=True, default='')
    total = models.CharField(_('Total'), max_length=200, blank=True, default='')
    date = models.DateTimeField(_('Creation date'))
    paid = models.BooleanField(_("Paid"), help_text=_('Invoice paid?'))

    def __unicode__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Receive Invoice')
        verbose_name_plural = _('Receives Invoices')

class Line(models.Model):
    """
    Line invoice model
    """
    invoice = models.ForeignKey(Invoice, related_name="line")
    reference = models.CharField(_('Reference'), max_length=200)
    concept = models.CharField(_('Concept'), max_length=200)
    quantity = models.CharField(_('Quantity'), max_length=200)
    unit = models.ForeignKey(QuantityUnit, related_name="quantityunit", blank=True, default='')
    unit_price = models.CharField(_('Unit Price'), max_length=200)
    amount = models.CharField(_('Ammount'), max_length=200)

    def __unicode__(self):
        return self.reference + " " + self.quantity + "x" + self.unit_price

    class Meta:
        verbose_name = _('Line')
        verbose_name_plural = _('Lines')

