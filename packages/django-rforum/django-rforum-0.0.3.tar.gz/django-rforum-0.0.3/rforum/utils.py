# -*- coding: utf-8 -*-
import models as mymodels
from django.contrib.auth.models import User
from django.conf import settings as conf


def es_moderador(usuario, topicslug):
    
    """
    Devuelve True si el usuario es moderador del foro al que corresponde el
    topic que le pasamos como parámetro o False si no lo es.
    """

    #print "--------------"
    #print usuario
    #print topicslug
    #import pdb; pdb.set_trace()

    #User.objects.get(username=usuario)
    if usuario.is_superuser:
        return True

    mytopic = mymodels.Topic.objects.get(slug=topicslug)
    moderators = mytopic.forum.moderators
    #print moderators.all()
    try:
        moderators.get(username=usuario)
        return True
    except User.DoesNotExist:
        return False


def grupo_moderadores(usuario):
    
    """
    Devuelve True si el usuario pertenece al grupo de moderadores 
    o False si no lo es.
    """

    #import pdb; pdb.set_trace()
    #User.objects.get(username=usuario)
    #import pdb; pdb.set_trace()
    qs = User.objects.filter(groups__name=conf.MODERATORS_GROUP_NAME, username=usuario.username)

    if qs:
        print "si"
        return True
    else:
        print "no"
        return False


