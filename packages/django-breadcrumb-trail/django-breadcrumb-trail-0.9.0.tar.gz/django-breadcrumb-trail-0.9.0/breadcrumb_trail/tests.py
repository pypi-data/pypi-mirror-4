from django.test import TestCase
#from django.test.client import RequestFactory
from breadcrumb_trail import breadcrumbs


class TestStuff(TestCase):
    #urls = 'breadcrumb_trail.urls'

    def test_something(self):
        print breadcrumbs('/')
