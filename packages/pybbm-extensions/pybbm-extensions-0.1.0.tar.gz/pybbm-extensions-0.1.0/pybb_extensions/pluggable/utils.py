#!/usr/bin/env python
# encoding: utf-8
import datetime


def get_datetime_now():
    try:
        from django.utils import timezone
        return timezone.now()
    except ImportError:
        return datetime.datetime.now()
