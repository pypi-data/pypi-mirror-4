# -*- coding: utf-8 -*-
from django import forms
import models as mymodels
from django.core.files.images import get_image_dimensions

class PostForm(forms.ModelForm):

    class Meta:
        model = mymodels.Post
        exclude = ('user_ip','status', 'date_created', 'date_modified', 'user', 'topic',)


class TopicForm(forms.Form):

    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = mymodels.UserProfile
        exclude = ('user',)
