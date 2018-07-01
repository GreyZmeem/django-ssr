import io
from unittest.mock import MagicMock

import requests
from django.http import HttpResponse
from django.test import TestCase

from django_ssr import backends


class PrerenderIOTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = backends.PrerenderIO

    def test_token_raises_value_error(self):
        with self.assertRaisesMessage(ValueError, 'prerender.io token is missing or empty'):
            self.backend()

    def test_token_in_headers(self):
        session = MagicMock()
        self.backend(token='token', session=MagicMock(return_value=session))
        session.headers.__setitem__.assert_called_once_with(self.backend.PRERENDER_TOKEN_HEADER_NAME, 'token')

    def test_render(self):
        resp = requests.Response()
        resp.status_code = 200
        resp.raw = io.BytesIO(b'<h1>Hello there.</h1>')

        session = MagicMock()
        session.get = MagicMock(return_value=resp)

        r = self.backend(token='token', session=MagicMock(return_value=session)).render('http://test/example')

        url = '%shttp://test/example' % self.backend.PRERENDER_IO_URL
        session.get.assert_called_once_with(url, allow_redirects=False)

        self.assertIsInstance(r, HttpResponse)
        self.assertEqual(200, r.status_code)
        self.assertEqual(b'<h1>Hello there.</h1>', r.content)
        self.assertEqual('21', r['content-length'])

    def test_update(self):
        resp = requests.Response()
        resp.status_code = 200

        session = MagicMock()
        session.post = MagicMock(return_value=resp)

        r = self.backend(token='token', session=MagicMock(return_value=session)).update('http://test/example')

        h = {'Content-Type': 'application/json'}
        d = {'url': 'http://test/example'}
        session.post.assert_called_once_with(self.backend.PRERENDER_IO_UPDATE_URL, d, headers=h)
        self.assertTrue(r)

    def test_update_is_false(self):
        resp = requests.Response()
        resp.status_code = 500

        session = MagicMock()
        session.post = MagicMock(return_value=resp)

        r = self.backend(token='token', session=MagicMock(return_value=session)).update('http://test/example')

        h = {'Content-Type': 'application/json'}
        d = {'url': 'http://test/example'}
        session.post.assert_called_once_with(self.backend.PRERENDER_IO_UPDATE_URL, d, headers=h)
        self.assertFalse(r)
