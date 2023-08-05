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


class Categories(models.Model):
    """
    Categories model
    """

    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=200)
    status =  models.BooleanField(_('Status'), default=True)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        datenow = int(time.time())
        super(Categories, self).save()

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Products(models.Model):
    """
    Products model
    """
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=200)
    category = models.ForeignKey(Categories, related_name="category", default=0)
    text = models.TextField(_('Text'))
    date_created = models.DateTimeField(_('Date Created'))
    date_modified = models.DateTimeField(_('Date Modified'))
    status =  models.BooleanField(_('Status'), default=True)
    hits = models.IntegerField(_('Hits'), blank=True, default=1)
    price = models.CharField(_('Price'), max_length=200, blank=True, default='0')


    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """datenow = int(time.time())
        if self.pk:
            self.date_modified = datenow
        else:
            self.date_created = datenow
            self.date_modified = datenow"""
        super(Products, self).save()

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')


class Images(models.Model):

    """
    Images model
    """

    product = models.ForeignKey(Products, related_name="images")
    image = models.ImageField(_('Image'), upload_to='images/products')
    status =  models.BooleanField(_('Status'), default=True)

    def __unicode__(self):
        return self.image.name

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
