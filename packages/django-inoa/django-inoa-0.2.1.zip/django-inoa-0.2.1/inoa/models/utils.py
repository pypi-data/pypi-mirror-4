# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.query import QuerySet

def default_repr(obj, extra_info=None):
    """
    Better default unicode representation for models, which includes the instance verbose name and ID.
    If the inoa app is in INSTALLED_APPS, this replaces all models' default __unicode__() method automatically.
    """
    if extra_info:
        return u"#%d: %s" % (obj.id, extra_info)
    else:
        return u"%s #%d" % (obj._meta.verbose_name.capitalize(), obj.id)

def clone_instance(obj):
    """
    Returns a new instance of obj's model, with the same attributes as obj.
    The new instance will not have been saved, and all primary keys will be cleared.
    """
    # Source: http://djangosnippets.org/snippets/904/ (modified with the first comment's suggestion)
    attributes = []
    for field in obj._meta.fields:
        if not field.primary_key and not field == obj._meta.pk:
            attr = (field.name, getattr(obj, field.name))
            attributes.append(attr)
    new_kwargs = dict(attributes);
    return obj.__class__.objects.create(**new_kwargs)

def has_changed(instance, field):
    """Returns True if the instance's given field was changed. Performs a database query."""
    # Source: http://zmsmith.com/2010/05/django-check-if-a-field-has-changed/
    if not instance.pk:
        return True
    old_value = instance.__class__._default_manager.\
             filter(pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value

def override_verbose_names(overrides):
    """
    Overrides the verbose_names of fields in the model class.
    Useful to change the verbose_names of fields from base classes.
    Parameter 'overrides' should be a {field name: verbose_name} dictionary.
    Should be used as a decorator on the model class.
    Note: only works when the base class has abstract = True.
    Example: @override_verbose_names({'timestamp': 'time of event occurence'})
    """
    def decorator(original_class):
        for field in original_class._meta.fields:
            if field.name in overrides:
                field.verbose_name = overrides[field.name]
        return original_class
    return decorator

def queryset_str_join(queryset, separator, text_if_empty=""):
    """
    Joins the queryset's elements into a string, in the same way as str.join(list).
    If the queryset is empty, returns the text_if_empty arguments (defaults to an empty string).
    """
    if queryset:
        return separator.join(map(lambda s: unicode(s), queryset))
    else:
        return text_if_empty
