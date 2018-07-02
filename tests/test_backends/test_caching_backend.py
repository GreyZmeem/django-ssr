import pickle

from django.http import HttpResponse
from django.test import TestCase

from django_ssr import backends


class Backend(backends.BackendBase):
    def render(self, url):
        return HttpResponse(b'<h1>Hello there!</h1>')

    def update(self, url: str):
        return True


class CachingBackend(backends.CachingBackendMixin, Backend):
    pass


class CachingBackendTestCase(TestCase):
    def setUp(self):
        self.backend = CachingBackend()
        self.backend.cache.clear()

    def test_response_is_cached(self):
        url = 'http://example.com/test'
        self.assertIsNone(self.backend.cache_retrieve(url))

        resp = self.backend.render(url)
        expected = HttpResponse(b'<h1>Hello there!</h1>')

        self.assertEqual(expected.content, resp.content)
        self.assertEqual(expected.content, self.backend.cache_retrieve(url).content)

    def test_response_is_retrieved_from_cache(self):
        url = 'http://example.com/test'
        expected = HttpResponse(b'Hello there!')
        self.backend.cache_set(url, expected)

        got = self.backend.render(url)
        self.assertEqual(expected.content, got.content)

    def test_unpickling_error(self):
        url = 'http://example.com/test'
        self.backend.cache.set(self.backend.cache_build_key(url), b'invalid')
        self.assertIsNone(self.backend.cache_retrieve(url))

    def test_unpickling_invalid_type(self):
        url = 'http://example.com/test'
        self.backend.cache.set(self.backend.cache_build_key(url), pickle.dumps('invalid'))
        self.assertIsNone(self.backend.cache_retrieve(url))

    def test_cache_cleared_on_update(self):
        url = 'http://example.com/test'
        self.backend.cache.set(self.backend.cache_build_key(url), 'response')

        self.backend.update(url)
        self.assertIsNone(self.backend.cache.get(self.backend.cache_build_key(url)))
