import re
from unittest.mock import MagicMock

from django.http import HttpResponse
from django.test import TestCase, RequestFactory

from django_ssr import middleware
from django_ssr.backends import BackendBase


class Backend(BackendBase):
    def render(self, url: str) -> HttpResponse:
        return HttpResponse(b'<h1>Hello there!</h1>', status=200)


class UserAgentMiddlewareTestCase(TestCase):
    def setUp(self):
        self.get_response = MagicMock()
        with self.settings(DJANGO_SSR_BACKEND='tests.test_middleware.test_user_agent.Backend'):
            self.middleware = middleware.UserAgentMiddleware(self.get_response)

    def test_rendered(self):
        req = RequestFactory().get('http://example.net', HTTP_USER_AGENT='Crawler')
        with self.settings(DJANGO_SSR_USER_AGENTS={re.compile('crawler', re.I)}):
            res = self.middleware(req)
        self.assertEqual(b'<h1>Hello there!</h1>', res.content)
        self.assertEqual(200, res.status_code)

    def test_not_rendered(self):
        req = RequestFactory().get('http://example.net', HTTP_USER_AGENT='Crawler')
        with self.settings(DJANGO_SSR_USER_AGENTS={re.compile('bot', re.I)}):
            res = self.middleware(req)
        self.get_response.assert_called_once_with(req)
        self.assertEqual(self.get_response(req), res)
