import io

import requests
from django.http import HttpResponse
from django.test import TestCase

from django_ssr import backends, settings


class RequestsDjangoResponseBuilderMixinTestCase(TestCase):
    def setUp(self):
        self.backend = backends.RequestsDjangoResponseBuilderMixin

    def test_build_django_response(self):
        resp = requests.Response()
        resp.status_code = 200
        resp.headers['content-type'] = 'text/html'
        resp.raw = io.BytesIO(b'<h1>Hello there.</h1>')

        r = self.backend().requests_response_to_django_response(resp)
        self.assertIsInstance(r, HttpResponse)
        self.assertEqual(200, r.status_code)
        self.assertEqual('text/html', r['content-type'])
        self.assertEqual('21', r['content-length'])
        self.assertEqual(b'<h1>Hello there.</h1>', r.content)

    def test_ignored_headers_are_removed(self):
        resp = requests.Response()
        resp.status_code = 200
        resp.raw = io.BytesIO(b'')
        for h in settings.REMOVE_HEADERS:
            resp.headers[h] = h

        r = self.backend().requests_response_to_django_response(resp)
        for h in settings.REMOVE_HEADERS:
            self.assertNotIn(h, r)
