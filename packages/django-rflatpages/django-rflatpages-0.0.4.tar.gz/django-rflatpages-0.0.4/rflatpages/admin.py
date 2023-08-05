# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels
import forms as myforms
import socket

class AdminPages(admin.ModelAdmin):
    exclude = ('user',)

    # http://www.userlinux.net/django-los-campos-tipo-slug.html
    prepopulated_fields = { 'slug': ['title'] }

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )

admin.site.register(mymodels.Pages, AdminPages)
