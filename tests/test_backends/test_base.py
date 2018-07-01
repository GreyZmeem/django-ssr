from django.test import RequestFactory, TestCase

from django_ssr import backends


class BaseBackendTestCase(TestCase):
    def setUp(self):
        self.backend = backends.BackendBase

    def test_build_absolute_url(self):
        req = RequestFactory().get('/main?test=1')
        self.assertEqual('http://testserver/main?test=1', self.backend().build_absolute_url(req))

    def test_build_absolute_url_strip_query_params(self):
        req = RequestFactory().get('/main?test=1')
        self.assertEqual('http://testserver/main', self.backend(strip_query_params=True).build_absolute_url(req))
