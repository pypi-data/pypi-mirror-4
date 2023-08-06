# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import models as mymodels

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        up = mymodels.UserProfile(user=user, twitter="@"+user.username)
        up.save()

post_save.connect(create_profile, sender=User)
