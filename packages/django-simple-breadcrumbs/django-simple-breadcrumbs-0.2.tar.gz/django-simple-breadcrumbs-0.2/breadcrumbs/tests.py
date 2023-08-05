import unittest
import django
from django.template import Context, Template
from mock import patch

def render(text, extra_context={}):
    c = Context()
    c.update(extra_context)
    return Template(text).render(c)

class BreadcrumbsTest(unittest.TestCase):
    def test_render_breadcrumb_without_url(self):
        result = render(
            '{% load breadcrumbs_tags %}'
            '{% breadcrumb "foo" bar %}'
        )
        self.assertEqual(result, '<span class="breadcrumbs-arrow"><img src="/media/images/arrow.gif" alt="Arrow"></span>&nbsp;&nbsp;foo')

    def test_render_breadcrumb_with_url(self):
        result = render(
            '{% load breadcrumbs_tags %}'
            '{% breadcrumb "foo" bar %}'
        , extra_context={"bar": "/some/url"})
        self.assertEqual(result, '<span class="breadcrumbs-arrow"><img src="/media/images/arrow.gif" alt="Arrow"></span><a href=\'/some/url\'>foo</a>')

    def test_render_breadcrumb_with_template(self):

        class MockTemplate(object):
            def render(self, c):
                return "foo"

        with patch.object(django.template.loader, 'get_template') as mock_get_template:
            mock_get_template.return_value = MockTemplate()
            result = render(
                '{% load breadcrumbs_tags %}'
                '{% breadcrumb "foo" bar %}'
            , extra_context={"bar": "http://nowhere"})
            self.assertEqual(result, "foo")
