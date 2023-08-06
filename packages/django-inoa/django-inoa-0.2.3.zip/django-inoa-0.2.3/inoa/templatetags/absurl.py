# -*- coding: utf-8 -*-

# Downloaded on 2011-07-03 from http://djangosnippets.org/snippets/1518/
# Edited with junckritter's change from http://djangosnippets.org/snippets/1518/#c2336

from django.contrib.sites.models import Site
from django.template import Library
from django.template.defaulttags import URLNode, url
import urlparse

register = Library()

def _absolutize(url):
    # domain = settings.ABSOLUTE_BASE_URL
    domain = "http://%s" % Site.objects.get_current().domain
    return urlparse.urljoin(domain, url)

class AbsoluteURLNode(URLNode):
    def render(self, context):
        url = super(AbsoluteURLNode, self).render(context)
        url = _absolutize(url)
        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

@register.tag
def absurl(parser, token, node_cls=AbsoluteURLNode):
    """Just like {% url %} but ads the domain of the current site."""
    node_instance = url(parser, token)
    return node_cls(view_name=node_instance.view_name,
        args=node_instance.args,
        kwargs=node_instance.kwargs,
        asvar=node_instance.asvar)

@register.filter
def absolutize(value):
    """Transforms a relative URL into an absolute URL."""
    return _absolutize(value)
