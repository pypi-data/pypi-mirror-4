# -*- coding: utf-8 -*-

from django import template
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.conf import settings as conf
from django.contrib.auth.models import User
import datetime
import random
import rforum.models as mymodels

register = template.Library()

@register.inclusion_tag('rforum/elements/widget_lastposts.html')
def last_posts(num):

    """
    Simple last_posts list
    """
    lastposts = mymodels.Post.objects.filter(status=1).order_by('-id')[:num]
    return { 'lastposts': lastposts }


@register.inclusion_tag('rforum/elements/widget_lastnews.html')
def last_news(num):

    """
    Simple last_posts list
    """
    forum = mymodels.Forum.objects.filter(status=1,visible=1,slug=conf.NEWS_FORUM).order_by('-id')
    topics = mymodels.Topic.objects.filter(forum=forum).order_by('-id')[:num]
    return { 'topics': topics }


@register.inclusion_tag('rforum/elements/widget_onlineusers.html')
def online_users(num):
    """
    Show user that has been login an hour ago.
      - http://djangosnippets.org/snippets/947/
      - http://mpcabd.igeex.biz/get-online-users-in-django/ (better implementation)
    """
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    sql_datetime = datetime.datetime.strftime(one_hour_ago, '%Y-%m-%d %H:%M:%S')
    users = User.objects.filter(last_login__gt=sql_datetime,
                                is_active__exact=1).order_by('-last_login')[:num]
    return { 'users': users, 'anon': random.randrange(60,78,1) }

@register.inclusion_tag('rforum/elements/widget_lastregisters.html')
def last_registers(num):
    """
    Show last registered users.
    """
    users = User.objects.filter(is_active__exact=1).order_by('-date_joined')[:num]
    return { 'users': users }

@register.inclusion_tag('rforum/elements/widget_lastlogins.html')
def last_logins(num):
    """
    Show last logins ...
    """
    users = User.objects.filter(is_active__exact=1).order_by('-last_login')[:num]
    return { 'users': users }


@register.inclusion_tag('rforum/elements/widget_stats.html')
def stats():
    """
    Show forum stats...
    """
    numposts = mymodels.Post.objects.filter(status=1)
    numtopics = mymodels.Topic.objects.all()
    numusers = User.objects.filter(is_active__exact=1)
    return { 'numusers': numusers.count, 'numposts': numposts.count, 'numtopics': numtopics.count, }
