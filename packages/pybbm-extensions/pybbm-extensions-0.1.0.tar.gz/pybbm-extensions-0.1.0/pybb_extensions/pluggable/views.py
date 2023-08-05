#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.views import generic
from pybb.views import PostEditMixin
from django.core.urlresolvers import reverse
from pybb import defaults


class AddPostView(PostEditMixin, generic.CreateView):

    def get_success_url(self):
        if (not self.request.user.is_authenticated()) and defaults.PYBB_PREMODERATION:
            return reverse('pybb:index')
        return super(AddPostView, self).get_success_url()
