# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket

class ImagesInline(admin.TabularInline):
    model = mymodels.Images


class AdminProducts(admin.ModelAdmin):
    # https://docs.djangoproject.com/en/dev/ref/contrib/admin/#inlinemodeladmin-objects
    inlines = [
        ImagesInline,
    ]

    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )


class AdminCategories(admin.ModelAdmin):
    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }


admin.site.register(mymodels.Products, AdminProducts)
admin.site.register(mymodels.Categories, AdminCategories)
