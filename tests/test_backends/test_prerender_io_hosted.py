import io
from unittest.mock import MagicMock

import requests
from django.http import HttpResponse
from django.test import TestCase

from django_ssr import backends


class PrerenderIOHostedTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = backends.PrerenderIOHosted

    def test_render_url_raises_value_error(self):
        with self.assertRaisesMessage(ValueError, 'Render url is missing or empty'):
            self.backend(render_url='')

    def test_update_url_raises_value_error(self):
        with self.assertRaisesMessage(ValueError, 'Update url is missing or empty'):
            self.backend(render_url='http://testserver', update_url='')

    def test_render(self):
        resp = requests.Response()
        resp.status_code = 200
        resp.raw = io.BytesIO(b'<h1>Hello there.</h1>')

        session = MagicMock()
        session.get = MagicMock(return_value=resp)

        s = MagicMock(return_value=session)
        b = self.backend(render_url='http://testserver/render/', update_url='http://testserver/update/', session=s)
        r = b.render('http://test/example')

        session.get.assert_called_once_with('http://testserver/render/http://test/example', allow_redirects=False)

        self.assertIsInstance(r, HttpResponse)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'<h1>Hello there.</h1>', r.content)
        self.assertEqual('21', r['content-length'])

    def test_update(self):
        resp = requests.Response()
        resp.status_code = 200

        session = MagicMock()
        session.post = MagicMock(return_value=resp)

        s = MagicMock(return_value=session)
        b = self.backend(render_url='http://testserver/render/', update_url='http://testserver/update/', session=s)
        r = b.update('http://test/example')

        h = {'Content-Type': 'application/json'}
        d = {'url': 'http://test/example'}
        session.post.assert_called_once_with('http://testserver/update/', json=d, headers=h)
        self.assertTrue(r)

    def test_update_is_false(self):
        resp = requests.Response()
        resp.status_code = 500

        session = MagicMock()
        session.post = MagicMock(return_value=resp)

        s = MagicMock(return_value=session)
        b = self.backend(render_url='http://testserver/render/', update_url='http://testserver/update/', session=s)
        r = b.update('http://test/example')

        h = {'Content-Type': 'application/json'}
        d = {'url': 'http://test/example'}
        session.post.assert_called_once_with('http://testserver/update/', json=d, headers=h)
        self.assertFalse(r)
