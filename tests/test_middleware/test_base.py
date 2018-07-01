from django.test import TestCase

from django_ssr import middleware
from django_ssr.backends import BackendBase


class Backend(BackendBase):
    pass


class BaseMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = middleware.BaseMiddleware

    def test_get_response_is_set(self):
        with self.settings(DJANGO_SSR_PRERENDER_IO_TOKEN='token'):
            self.assertEqual('get_response', self.middleware('get_response').get_response)

    def test_backend_from_settings(self):
        with self.settings(DJANGO_SSR_BACKEND='tests.test_middleware.test_base.Backend'):
            self.assertIsInstance(self.middleware('get_response').backend, Backend)

    def test_backend_as_param(self):
        self.assertIsInstance(self.middleware('get_response', backend=Backend).backend, Backend)

    def test_must_render_called(self):
        with self.settings(DJANGO_SSR_PRERENDER_IO_TOKEN='token'):
            with self.assertRaisesMessage(NotImplementedError, 'BaseMiddleware.must_render'):
                self.middleware('get_response')('request')
