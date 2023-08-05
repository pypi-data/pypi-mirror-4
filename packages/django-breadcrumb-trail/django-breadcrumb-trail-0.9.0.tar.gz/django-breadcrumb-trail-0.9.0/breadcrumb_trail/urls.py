from django.conf.urls import patterns, url
from breadcrumb_trail import views

urlpatterns = patterns('',
    url(r'^$', views.root),
    url(r'^comments?$', views.comment_list),
    url(r'^comments/1$', views.comment_detail),
    url(r'^articles$', views.ArticleList.as_view()),
    url(r'^articles/1$', views.ArticleDetail.as_view()),
)
