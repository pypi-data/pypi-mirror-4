# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rforum.views import *

"""
Todas las llamadas que lleven un argumento 'topicslug' pasan por un middleware
(siempre que esté configurado en settings) que comprueba si el usuario activo
tiene permisos de administrador para el Forum de ese Topic, así nos aseguramos
de que nunca se pasen por alto los permisos de moderadores.

Por defecto los administradores también son moderadores. Ojo, porque si en
alguna acción que tenga que pasar por middleware no llamamos "topicslug" al
parámetro, no pasará.
"""

urlpatterns = patterns('',
    url(r'^$',                     ForumListView.as_view(), {}, 'app_forum-forum-index'),
    url(r'^(?P<slug>[-\w]+)/$',    ForumDetailView.as_view(), {}, "app_forum-forum-detail"),

    url(r'^(?P<slug>[-\w]+)/(?P<slug2>[-\w]+).html$',                  TopicListView.as_view(), {}, "app_forum-topic-list"),
    url(r'^add-topic/(?P<slug>[-\w]+)/$',                              TopicCreate.as_view(), {}, "app_forum-topic-add"),
    url(r'^openclose-topic/(?P<topicslug>[-\w]+)/(?P<action>[-\w]+)$', TopicAction.as_view(), {}, "app_forum-topic-action"), # topicslug, pasa por middleware
    url(r'^delete-topic/(?P<topicslug>[-\w]+)/$',                      TopicDelete.as_view(), {}, "app_forum-topic-delete"), # topicslug, pasa por middleware

    url(r'^add-post/(?P<slug>[-\w]+)/$',                        PostCreate.as_view(), {}, "app_forum-post-add"),
    url(r'^edit-post/(?P<topicslug>[-\w]+)/(?P<id>[-\w]+)$',    PostUpdate.as_view(), {}, "app_forum-post-edit"),   # topicslug, pasa por middleware
    url(r'^delete-post/(?P<topicslug>[-\w]+)/(?P<id>[-\w]+)$',  PostDelete.as_view(), {}, "app_forum-post-delete"), # topicslug, pasa por middleware

    url(r'^user/(?P<user>[-\w]+)/$',                            UserProfileView.as_view(), {}, "app_forum-userprofile"),

)
