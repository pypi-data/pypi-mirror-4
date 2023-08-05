from django.views.generic import View
from django.http import HttpResponse
from django.template import Template, Context

template_str = """
{% load breadcrumbs %}
<!DOCTYPE html>
<html>
  <head>
    <title>Django Breadcrumb Trail</title>
    <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.1.1/css/bootstrap.no-icons.min.css" rel="stylesheet">
  </head>
  <body>
    <div class="container">
      <h1>Django Breadcrumb Trail</h1>
      <div>{% breadcrumbs request %}</div>
      <div class="well">
      <ul>
      <li><a href="/">/</a></li>
      <li><a href="/comments">/comments</a></li>
      <li><a href="/comments/1">/comments/1</a></li>
      <li><a href="/articles">/articles</a></li>
      <li><a href="/articles/1">/articles/1</a></li>
      </ul>
      </div>
    </div>
  </body>
</html>
"""


def root(request):
    context = Context({'request': request})
    content = Template(template_str).render(context)
    return HttpResponse(content)


def comment_list(request):
    context = Context({'request': request})
    content = Template(template_str).render(context)
    return HttpResponse(content)


def comment_detail(request):
    context = Context({'request': request})
    content = Template(template_str).render(context)
    return HttpResponse(content)


class ArticleList(View):
    def get(self, request):
        context = Context({'request': request})
        content = Template(template_str).render(context)
        return HttpResponse(content)


class ArticleDetail(View):
    def get(self, request):
        context = Context({'request': request})
        content = Template(template_str).render(context)
        return HttpResponse(content)
