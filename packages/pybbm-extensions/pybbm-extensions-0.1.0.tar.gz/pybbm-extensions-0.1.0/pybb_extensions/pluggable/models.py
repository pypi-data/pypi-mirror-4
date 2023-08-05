#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.manager import Manager
from django.db.models.signals import post_save
from pybb.models import Topic, Post
from pybb_extensions.pluggable.utils import get_datetime_now
from django.utils.html import strip_tags

registry = []


class PlugManager(Manager):

    def _default_qs(self):
        return super(PlugManager, self).get_query_set()

    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj.__class__)
        try:
            return self._default_qs().get(content_type=ctype, object_id=obj.id)
        except:
            return None

    def create_for_object(self, obj, forum_id, topic=None, user=None, body=None):
        try:
            name = obj.forum_topic_title()
        except:
            name = str(obj)

        try:
            added = obj.forum_topic_added()
        except:
            added = get_datetime_now()

        try:
            user = obj.forum_topic_user()
        except:
            try:
                user = obj.user
            except:
                user = User.objects.filter(is_superuser=True).order_by('id')[0].get()

        if not body:
            try:
                body = obj.forum_topic_body()
            except:
                body = str(obj)

        if not topic:
            topic = Topic.objects.create(forum_id=forum_id, user=user, name=name)
            topic.created = added
            topic.save()
        first_post, created = Post.objects.get_or_create(topic_id=topic.id, user=user, body=body, body_html=body, body_text=strip_tags(body), created=added)

        ctype = ContentType.objects.get_for_model(obj.__class__)
        return super(PlugManager, self).create(topic_id=topic.id, content_type=ctype, object_id=obj.id)


class Plug(models.Model):
    topic = models.OneToOneField(Topic, related_name='plug')
    content_type = models.ForeignKey(ContentType)
    object_id = models.IntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    objects = PlugManager()

    class Meta:
        db_table = 'pybb_ext_plug'
        unique_together = ('content_type', 'object_id')

    def content_url(self):
        try:
            return self.content_object.get_absolute_url()
        except:
            return None

    def posts(self):
        posts = Post.objects.filter(topic=self.topic)
        return posts

    @classmethod
    def create_topic(cls):
        pass


class AlreadyRegistered(Exception):
    pass


def register(model, attr="plug"):
    if model in registry:
        raise AlreadyRegistered(('The model %s has already been registered.') % model.__name__)
    if not hasattr(model, 'forum_id'):
        raise Exception('You must specify a forum_id() method in model %s.' % model.__name__)
    registry.append(model)

    def get_plug_for_instance(self):
        return Plug.objects.get_for_object(self)

    model.add_to_class('plug', get_plug_for_instance)
    post_save.connect(plug_signal_handler, sender=model)


def plug_signal_handler(sender, instance, **kwargs):
    if kwargs.get('created', False):
        Plug.objects.create_for_object(instance, instance.forum_id())
