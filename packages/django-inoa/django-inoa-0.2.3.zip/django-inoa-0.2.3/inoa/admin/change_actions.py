# -*- coding: utf-8 -*-

"""
Allows you to have per-instance admin actions in the change_form (item detail) view,
in the same vein as the actions in the change_list view (items list).


#######
 USAGE 
#######

Add 'inoa' to the INSTALLED_APPS.

Include ChangeActionsAdmin in the base classes of your admin class, before ModelAdmin.
Example: class MyAdmin(ChangeActionsAdmin, admin.ModelAdmin):

Then, define a "change_actions" list or tuple in your ModelAdmin class,
just like you would define the "actions" attribute.
Example: change_actions = ('my_function', my_other_function)

Your functions or methods should take three arguments:
my_function(modeladmin, request, obj)

If your function returns a subclass of HttpResponse, it will be returned to the user.
Otherwise, processing will continue as if the user had hit the "Save and Continue" button.

If your ModelAdmin class contains a change_actions_text attribute, it will be displayed
to the left of the buttons. It may also be a callable, taking the same arguments as the other methods.

Note that the instance will be updated (saved) with data from the form BEFORE your function is called.


#########
 OPTIONS 
#########

function.short_description = u"Button name"
# Changes the text in the button.

function.return_to_list = True
# Redirects the user to the objects list (change_list) afterwards.

function.enable_condition = method(modeladmin, request, obj=None)
# Method called to check if the action should be enabled or not.
# Note that it will be called twice: before displaying the change page, and after the button is hit.
# It must return True in both occasions for the action to occur. 
""" 

from django.http import HttpResponse
from django.template.loader import select_template, get_template


class ChangeActionsAdmin(object):
    """Mixin class to be inserted before ModelAdmin. Allows change_form actions in the admin."""
    
    def get_change_actions(self, request, obj):
        if not hasattr(self, 'change_actions'):
            return []
        change_actions = []
        for item in self.change_actions:
            action = self.get_action(item)
            if not action:
                continue
            enable_condition = getattr(action[0], 'enable_condition', None)
            if enable_condition and not self.call_bound(request, obj, enable_condition):
                continue
            change_actions.append(action)
        return change_actions
    
    def get_change_actions_text(self, request, obj):
        change_actions_text = getattr(self, 'change_actions_text', "")
        if callable(change_actions_text):
            change_actions_text = self.call_bound(request, obj, change_actions_text)
        return change_actions_text or ""
    
    def call_bound(self, request, obj, method):
        if hasattr(method, '__self__'):
            return method(request, obj)
        else:
            return method(self, request, obj)
    
    def response_change(self, request, obj, *args, **kwargs):
        actions = self.get_change_actions(request, obj)
        for action in actions:
            if 'action-' + action[1] in request.POST:
                response = action[0](self, request, obj)
                if isinstance(response, HttpResponse):
                    return response
                if not getattr(action[0], 'return_to_list', False):
                    request.POST['_continue'] = True
                else:
                    request.POST.pop('_continue', None)
        
        return super(ChangeActionsAdmin, self).response_change(request, obj, *args, **kwargs)
    
    def render_change_form(self, request, context, *args, **kwargs):
        opts = self.model._meta
        app_label = opts.app_label
        change_form_template_backup = self.change_form_template
        self.change_form_template = "admin/change_form_with_actions.html"
        
        change_form_base_template = change_form_template_backup or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ]
        if isinstance(change_form_base_template, (list, tuple)):
            change_form_base_template = select_template(change_form_base_template)
        else:
            change_form_base_template = get_template(change_form_base_template)
        
        obj = kwargs.get('obj', None)
        context['change_actions'] = self.get_change_actions(request, obj)
        context['change_actions_text'] = self.get_change_actions_text(request, obj)
        context['change_form_base_template'] = change_form_base_template
        
        response = super(ChangeActionsAdmin, self).render_change_form(request, context, *args, **kwargs)
        self.change_form_template = change_form_template_backup
        return response
