#!/usr/bin/python
# -*- coding: utf-8 -*-
from django import template
from pybb.forms import PostForm, AdminPostForm
from pybb.models import Post
from pybb_extensions.pluggable.models import Plug, registry
register = template.Library()


@register.inclusion_tag("pybb_extensions/pluggable/topic.html")
def pluggable_topic(obj, user=None):
    plug = Plug.objects.get_for_object(obj)
    if plug:
        return {'posts': plug.posts, 'topic': plug.topic, 'user': user, }
    return {'user': user, }


@register.inclusion_tag("pybb_extensions/pluggable/form.html")
def pluggable_topic_form(obj, user=None):
    plug = Plug.objects.get_for_object(obj)
    if plug:
        if user.is_staff:
            form = AdminPostForm(initial={'login': user.username}, topic=plug.topic)
        else:
            form = PostForm(topic=plug.topic)
        return {'plug': plug, 'topic': plug.topic, 'form': form, 'user': user, }
    return {'user': user, }
