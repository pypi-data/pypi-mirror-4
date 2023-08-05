from haystack import site
from haystack.fields import CharField, DateTimeField, EdgeNgramField
from haystack.indexes import RealTimeSearchIndex
from pybb.models import Topic
import datetime


class PybbTopicIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    name = CharField(model_attr='title')
    #user = CharField(model_attr='user')
    #category = CharField(model_attr='category')
    created = DateTimeField(model_attr='created')
    content_auto = EdgeNgramField(model_attr='title')

    def get_updated_field(self):
        return "date_added"

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Topic.objects.filter(forum__hidden=False).filter(created__lte=datetime.datetime.now())


site.register(Topic, PybbTopicIndex)

"""
class PybbPostIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    name = CharField(model_attr='name')
    #user = CharField(model_attr='user')
    #category = CharField(model_attr='category')
    created = DateTimeField(model_attr='created')
    content_auto = EdgeNgramField(model_attr='title')

    def get_updated_field(self):
        return "date_added"

    def index_queryset(self):        
        return Blog.objects.filter(date_added__lte=datetime.datetime.now(), active=True)

site.register(Blog, PybbPostIndex)
"""
