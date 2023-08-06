# -*- coding: utf-8 -*-

from functools import partial
from django.forms import MediaDefiningClass

"""
This code is a community effort, and it was based on two StackOverflow questions and their references.

http://stackoverflow.com/questions/6473340/link-to-foreignkey-in-admin-causes-attributeerror-when-debug-is-false
http://stackoverflow.com/questions/6473340/link-to-foreignkey-in-admin-causes-attributeerror-when-debug-is-false/7192721#7192721

We have put together those codes, made some adjustments an extended it to suport ManyToMany ralationships
also as a list of links in the admin.
We have also changed the link marker from a preceding 'link_to_' to a trailing ':as_link' to improe readability.
"""

"""
Creates navigable links for ManyToManyField and ForeignKey in the change_list view.

Usage:
1. Your ModelAdmin class must inherit from FKLinkMixin.
   Alternatively, set the ModelAdmin's __metaclass__ attribute to FKLinkMetaclass.
2. Append ':as_link' to the names of ForeignKey or ManyToManyField fields
   in the 'list_display', 'readoly_fields' or 'fields' attribute.

Note: you may use __ to display the related instance's attributes
      e.g. 'author__name:as_link'.
"""
           
class FKLinkMetaclass(MediaDefiningClass):
    def __new__(cls, name, bases, attrs):
        new_class = super(
            FKLinkMetaclass, cls).__new__(cls, name, bases, attrs)
        
        def link_generator(instance, field):
            #Tests for ManyRelated navigation
            base = getattr(instance, field.split("__")[0])

            for other_field in field.split("__")[1:]:
                base = base.__dict__[other_field]
                
            if base.__class__.__name__ == "ManyRelatedManager":
                return many_to_many_links(instance, field, base)
            else:
                return foreign_key_link(instance, field)
             
             
        def foreign_key_link(instance, field):
            return generate_item_html(getattr(instance, field))
        
        
        def many_to_many_links(instance, field, base):
            html = u"<div style='max-height: 100px; overflow:auto;'><ul>"
            for item in base.all():
                html += generate_item_html(item)
            return html + u"</ul></div>"
            
        
        def generate_item_html(item):
            return u'<li><a href="../../%s/%s/%d">%s</a></li>' % (item._meta.app_label, item._meta.module_name,
                                                                 item.id, unicode(item))
            
            
        def _add_method(name):
            if name is None: return
            
            if isinstance(name, basestring) and name[-8:] == ':as_link':
                name_without_marker = name[:-8]
                                
                method = partial(link_generator, field=name_without_marker)
                method.__name__ = name_without_marker
                method.allow_tags = True
                setattr(new_class, name, method)
                

        #make this work for InlineModelAdmin classes as well, who do not have a
        #.list_display attribute
        if hasattr(new_class, "list_display") and new_class.list_display is not None:
            for name in new_class.list_display:
                _add_method(name)
        
        #enable the 'link_to_<foreignKeyModel>' syntax for the ModelAdmin.readonly_fields
        if hasattr(new_class, "readonly_fields") and new_class.readonly_fields is not None:
            for name in new_class.readonly_fields:
                _add_method(name)
        
        #enable the 'link_to_<foreignKeyModel>' syntax for the ModelAdmin.fields
        if hasattr(new_class, "fields") and new_class.fields is not None:
            for name in new_class.fields:
                _add_method(name)

        return new_class


class FKLinkMixin(object):
    __metaclass__ = FKLinkMetaclass
