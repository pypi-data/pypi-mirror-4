# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.query import QuerySet

"""
Allows navigation from instances of a base non-abstract class (multi-table inheritance)
to the appropriate derived instances.

Usage:
1. Your base model class should inherit from ParentModel rather than models.Model.
2. Add an attribute in your base model class (suggested name: children) set to ChildManager()
3. Define a get_parent_model() method in the base model class, which returns your base class.

Example:

class Post(ParentModel):
    title = models.CharField(max_length=50)

    objects = models.Manager()
    children = ChildManager()

    def __unicode__(self):
        return self.title

    def get_parent_model(self):
        return Post

class Article(Post):
    text = models.TextField()
    short_name = "post"

class Photo(Post):
    image = models.ImageField(upload_to='photos/')
    short_name = "photo"

class Link(Post):
    url = models.URLField()
    short_name = "link"

In this case, the Post.children manager will return a queryset containing
instances of the appropriate child model, rather than instances of Post.

>>> Post.objects.all()
[<Post: Django>, <Post: Make a Tumblelog>, <Post: Self Portrait>]

>>> Post.children.all()
[<Link: Django>, <Article: Make a Tumblelog>, <Photo: Self Portrait>]
"""

class ChildQuerySet(QuerySet):
    def iterator(self):
        for obj in super(ChildQuerySet, self).iterator():
            yield obj.get_child_object()

class ChildManager(models.Manager):
    def get_query_set(self):
        return ChildQuerySet(self.model)

class ParentModel(models.Model):
    _child_name = models.CharField(max_length=100, editable=False)
    short_name = u"(subtipo desconhecido)"  # TODO: Internationalize.

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self._child_name = self.get_child_name()
        super(ParentModel, self).save(*args, **kwargs)

    def get_child_name(self):
        if type(self) is self.get_parent_model():
            return self._child_name
        return self.__class__.__name__.lower()

    def get_child_object(self, selfOnNoChild=False):
        child_name = self.get_child_name()
        if child_name:
            return getattr(self, child_name)
        else:
            return self if selfOnNoChild else None

    def get_parent_link(self):
        return self._meta.parents[self.get_parent_model()]

    def get_parent_model(self):
        raise NotImplementedError

    def get_parent_object(self):
        return getattr(self, self.get_parent_link().name)
    
    def __unicode__(self):
        child = obj.get_child_object()
        if child and child != obj:
            return u"Base para %s %s" % (child.short_name, child)  # TODO: Internationalize.
        else:
            return default_repr(obj)
    