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

class Pages(models.Model):

    """
    Pages model
    """

    user = models.ForeignKey(User, related_name="page_from")
    title = models.CharField(_('Title'), max_length=255)
    slug = models.CharField(_('Slug'), max_length=200)
    text = models.TextField(_('Text'))
    date_created = models.DateTimeField(_('Date Created'))
    date_modified = models.DateTimeField(_('Date Modified'))
    ip = models.CharField(_('IP'), max_length=100)
    hits = models.IntegerField(_('Hits'))
    status =  models.BooleanField(_('Status'), default=True)
    template = models.CharField(_('Render template'), max_length=100,
        choices=conf.RFLAT_TEMPLATES, blank=True)

    def __unicode__(self):
        return self.slug

    def save(self, *args, **kwargs):
        datenow = int(time.time())
        """if self.pk:
            self.date_modified = datenow
        else:
            self.date_created = datenow
            self.date_modified = datenow"""
        self.ip = socket.gethostbyname(socket.gethostname())
        super(Pages, self).save()

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
