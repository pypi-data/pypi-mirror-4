# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rshop.views import ShopIndexView, ProductDetailView, sendAnEmail

# Llamamos al registro a traves del formulario RegisterForm que hemos creado
urlpatterns = patterns('',
    url(r'^$',                                     ShopIndexView.as_view(), {}, 'app_shop-index'),
    url(r'^page/(?P<page>\d+)/$',                  ShopIndexView.as_view(), {}, 'app_shop-index-page'),
    url(r'^(?P<slug>[-\w]+)\.html$',               ProductDetailView.as_view(), {}, 'app_shop-product-detail'),
    url(r'^sendAnEmail/$',						   sendAnEmail, {}, 'app_shop-email'),
)
