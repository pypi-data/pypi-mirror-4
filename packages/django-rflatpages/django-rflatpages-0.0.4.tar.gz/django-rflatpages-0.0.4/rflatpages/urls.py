# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rflatpages.views import FlatpageDetailView

# Llamamos al registro a traves del formulario RegisterForm que hemos creado
urlpatterns = patterns('',
    url(r'^$',                      FlatpageDetailView.as_view(), {'slug': 'start'}, 'app_flatpage-detail'),
    url(r'^(?P<slug>[-\w/]+)/$',    FlatpageDetailView.as_view(), {}, 'app_flatpage-detail'),

)
