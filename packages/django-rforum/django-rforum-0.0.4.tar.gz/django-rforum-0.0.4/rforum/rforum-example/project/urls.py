# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponseRedirect
import os
from rforum.views import UserProfile
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    # Admin
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/filebrowser/', include('filebrowser.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # App_Foro
    url(r'^rforum/', include('rforum.urls')),
    url(r'^accounts/profile/$', UserProfile.as_view(), {}, "account_profile"), # App_Foro UserProfile

    # Accounts (Django-AllAuth)
    url(r'^accounts/', include('allauth.urls')),

)

# Media files (only for devel)
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
