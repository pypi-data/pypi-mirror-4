# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib.sites.models import Site
import models as mymodels
import forms as myforms
from django.core.mail import EmailMessage

from django.conf import settings as conf

from django.views.generic import DetailView, ListView

class ShopIndexView(ListView):

    template_name = "rshop/index.html"
    context_object_name = "myproducts"
    paginate_by = 20

    def __init__(self):
        pass

    def get_queryset(self):
        self.obj = mymodels.Products.objects.all().filter(status=1).order_by('-date_created')
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(ShopIndexView, self).get_context_data(**kwargs)
        context.update({
            'title': _('Shop'),
            'description': conf.SITE_DESCRIPTION,
        })
        return context


class ProductDetailView(DetailView):

    template_name = "rshop/detail.html"
    context_object_name = "myproduct"
    paginate_by = 20

    def __init__(self):
        pass

    def get_object(self):
        self.obj = get_object_or_404(mymodels.Products, slug=self.kwargs['slug'], status=1)
        self.obj.hits = self.obj.hits + 1
        self.obj.save()
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context.update({
            'title': self.obj.title,
        })
        return context

def sendAnEmail(request):

    if request.method == 'POST': # If the form has been submitted...
        texto = "<ul>"
        for i in request.POST:
            texto = texto + "<li>" + i +": "+ request.POST[i] + "</li>"
        texto = texto + "</ul>"
    email = EmailMessage(_('New order!'), texto, to=[conf.SITE_CONTACT_EMAIL])
    email.content_subtype = "html"  # Main content is now text/html
    email.send()
    return redirect('app_shop-index')