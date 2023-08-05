#!/usr/bin/env python
# encoding: utf-8
from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase
from django.test.client import Client
from pybb.models import Forum, Category, Topic
from pybb_extensions.pluggable.models import register, AlreadyRegistered, Plug, \
    registry
from pybb_extensions.pluggable.utils import get_datetime_now


class Bogus(models.Model):
    title = models.CharField(max_length=3)
    user = models.ForeignKey(User)
    added = models.DateTimeField(default=get_datetime_now())

    def __unicode__(self):
        return self.title

    def forum_id(self):
        return 1

    def forum_topic_title(self):
        return self.title

    def forum_topic_body(self):
        return 'yo'

    def forum_topic_added(self):
        return self.added


class BogusTwo(models.Model):
    title = models.CharField(max_length=3)
    user = models.ForeignKey(User)
    added = models.DateTimeField(default=get_datetime_now())

    def forum_id(self):
        return 1


class BBPlugTests(TestCase):

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        user, created = User.objects.get_or_create(username='zalew')
        user.set_password('test')
        user.save()
        self.user = user
        Forum.objects.create(id=1, category=Category.objects.create(id=1))

    def test_plug(self):
        register(Bogus)
        with self.assertRaises(AlreadyRegistered) as e:
            register(Bogus)

        self.assertTrue(hasattr(Bogus, 'plug'))

        b, cr = Bogus.objects.get_or_create(id=1, user=self.user, title='elo elo')
        self.assertTrue(hasattr(b, 'plug'))
        self.assertTrue(isinstance(b.plug(), Plug))
        self.assertEqual(b.plug().topic.forum.id, 1)
        self.assertEqual(b.plug().topic.name, 'elo elo')
        self.assertEqual(b.plug().topic.head.body, 'yo')
        self.assertEqual(b.plug().topic.user, b.user)
        self.assertEqual(b.plug().topic.created, b.added)

    def test_plug_topic(self):

        b, cr = BogusTwo.objects.get_or_create(id=2, user=self.user, title='siema nara')
        topic = Topic.objects.create(forum_id=1, name=b.title, user=b.user)
        topic.created = b.added
        topic.updated = b.added
        topic.save()

        self.assertEqual(Plug.objects.get_for_object(b), None)

        plug = Plug.objects.create_for_object(b, 1, topic=topic, body='hello')

        self.assertEqual(plug.topic.forum.id, 1)
        self.assertEqual(plug.topic.name, 'siema nara')
        self.assertEqual(plug.topic.user, b.user)
        self.assertEqual(plug.topic.created, b.added)
        self.assertEqual(plug.topic.head.body, 'hello')

        self.assertFalse(hasattr(b, 'plug'))
        register(BogusTwo)
        self.assertTrue(hasattr(b, 'plug'))
        self.assertTrue(isinstance(b.plug(), Plug))

        self.assertEqual(Plug.objects.get_for_object(b), plug)
