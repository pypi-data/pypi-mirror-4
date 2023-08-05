# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib.sites.models import Site
from django.utils.translation import activate
import models as mymodels
import forms as myforms

from django.conf import settings as conf

from django.views.generic import DetailView
from wkhtmltopdf.views import PDFTemplateView

def changelang(request, code):
    from django.utils.translation import check_for_language, activate, to_locale, get_language
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    lang_code = code
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response


class PDFInvoiceDetailView(PDFTemplateView):

    # filename = 'my_pdf.pdf'
    template_name = "rinvoices/default.html"
    context_object_name = "myinvoice"

    def __init__(self):
        pass

    def get_context_data(self, **kwargs):
        lang = self.kwargs.get('lang', 'es')
        changelang(self.request, lang)
        myinvoice = get_object_or_404(mymodels.Invoice, id=self.kwargs['id'])
        return {'myinvoice': myinvoice}


class InvoiceDetailView(DetailView):

    # template_name=model.objects.get()
    # page = get_object_or_404(mymodels.Pages, slug=self.kwargs['render_template']);
    # template_name = page.template_name

    template_name = "rinvoices/default.html"
    context_object_name = "myinvoice"

    def __init__(self):
        pass

    def get_object(self):
        lang = self.kwargs.get('lang', 'es')
        changelang(self.request, lang)
        myinvoice = get_object_or_404(mymodels.Invoice, id=self.kwargs['id'])
        return myinvoice


