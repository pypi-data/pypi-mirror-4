from breadcrumb_trail import breadcrumbs as request_to_breadcrumbs
from django import template


register = template.Library()


@register.inclusion_tag('breadcrumbs.html')
def breadcrumbs(request):
    return {'breadcrumbs': request_to_breadcrumbs(request)}
