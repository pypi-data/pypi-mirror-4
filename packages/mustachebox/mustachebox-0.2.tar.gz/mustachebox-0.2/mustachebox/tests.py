"""
Here we test the example_bakends methods
"""

from django.test import TestCase
from django.test.client import Client
from django import template
from django.template import TemplateSyntaxError


class TestGraphList(TestCase):

    def test_response(self):
        """
        Check if the url showing all the graph is responding
        """
        client = Client()
        response = client.get("/grapher/all/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context['object_list']), 6)


class TestTemplateTags(TestCase):

    def test_area(self):
        t = template.Template("{% load graph %} {% graph area %}")
        c = template.Context({"STATIC_URL": "/static/"})
        self.assertIsNot(len(t.render(c)), 0)

    def test_bar_chart(self):
        t = template.Template("{% load graph %} {% graph bar_chart %}")
        c = template.Context({"STATIC_URL": "/static/"})
        self.assertIsNot(len(t.render(c)), 0)

    def test_column_chart(self):
        t = template.Template("{% load graph %} {% graph column_chart %}")
        c = template.Context({"STATIC_URL": "/static/"})
        self.assertIsNot(len(t.render(c)), 0)

    def test_pie_chart(self):
        t = template.Template("{% load graph %} {% graph pie_chart %}")
        c = template.Context({"STATIC_URL": "/static/"})
        self.assertIsNot(len(t.render(c)), 0)

    def test_line_chart(self):
        t = template.Template("{% load graph %} {% graph line_chart %}")
        c = template.Context({"STATIC_URL": "/static/"})
        self.assertIsNot(len(t.render(c)), 0)


class TestGraphPages(TestCase):

    def test_ajax(self):
        client = Client()
        response = self.client.get("/grapher/area/",
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response._headers['content-type'][1],
                         'application/json')

    def test_area(self):
        client = Client()
        response = client.get("/grapher/area/")
        self.assertEqual(response.status_code, 200)

    def test_bar_chart(self):
        client = Client()
        response = client.get("/grapher/bar_chart/")
        self.assertEqual(response.status_code, 200)

    def test_column_chart(self):
        client = Client()
        response = client.get("/grapher/column_chart/")
        self.assertEqual(response.status_code, 200)

    def test_pie_chart(self):
        client = Client()
        response = client.get("/grapher/pie_chart/")
        self.assertEqual(response.status_code, 200)

    def test_line_chart(self):
        client = Client()
        response = client.get("/grapher/line_chart/")
        self.assertEqual(response.status_code, 200)

    def test_404(self):
        client = Client()
        response = client.get("/grapher/this_chart_does_not_exist/")
        self.assertEqual(response.status_code, 404)
