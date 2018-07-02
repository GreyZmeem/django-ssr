import hashlib
import logging
import pickle
from typing import Callable, Optional
from urllib.parse import urlparse, ParseResult

import requests
from django.core.cache import caches, BaseCache
from django.http import HttpRequest, HttpResponse
from django.utils.encoding import force_bytes

from django_ssr import settings

__all__ = [
    'BackendBase',
    'PrerenderIOHosted',
    'PrerenderIO',
]

logger = logging.getLogger(__name__)
SessionCreator = Callable[..., requests.Session]


class BackendBase:
    """
    Base class for all SSR's.
    """

    def __init__(self, *, strip_query_params: bool = settings.STRIP_QUERY_PARAMS, **kwargs):
        self.strip_query_params = strip_query_params

    def build_absolute_url(self, request: HttpRequest) -> str:
        """
        Return the fully-qualified url that will be pre-rendered.
        """
        url = request.build_absolute_uri()
        if self.strip_query_params:
            parts = urlparse(url)  # type: ParseResult
            url = '%s://%s%s' % (parts.scheme, parts.netloc, parts.path)
        return url

    def render(self, url: str) -> HttpResponse:
        """
        Return an HttpResponse, passing through all headers and the status code.
        """
        raise NotImplementedError

    def update(self, url: str) -> bool:
        """
        Force an update of the cache for a particular URL.
        """
        raise NotImplementedError


class RequestsDjangoResponseBuilderMixin:
    def requests_response_to_django_response(self, response: requests.Response) -> HttpResponse:
        """
        Build django's response from request's response.
        """
        r = HttpResponse(response.content)
        for k, v in response.headers.items():
            if k.lower() not in settings.REMOVE_HEADERS:
                r[k] = v
        r['content-length'] = len(response.content)
        r.status_code = response.status_code
        return r


class CachingBackendMixin:
    """
    Store rendered pages in django's cache
    """

    def __init__(
        self,
        *,
        cache_alias: str = None,
        cache_prefix: str = None,
        cache_timeout: int = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.cache = caches[cache_alias if cache_alias is not None else settings.CACHE_ALIAS]  # type: BaseCache
        self.cache_prefix = cache_prefix if cache_prefix is not None else settings.CACHE_PREFIX
        self.cache_timeout = cache_timeout if cache_timeout is not None else settings.CACHE_TIMEOUT

    def render(self, url: str) -> HttpResponse:
        """
        Return an HttpResponse, passing through all headers and the status code.
        """
        resp = self.cache_retrieve(url)
        if resp is None:
            resp = super().render(url)
            self.cache_set(url, resp)
        return resp

    def update(self, url: str) -> bool:
        """
        Force an update of the cache for a particular URL.
        """
        is_ok = super().update(url)
        if is_ok:
            self.cache_clear(url)
        return is_ok

    def cache_build_key(self, url: str) -> str:
        """
        Return key under which response will be saved or retrieved.
        """
        url_hash = hashlib.md5(force_bytes(url)).hexdigest()
        return '%s:%s' % (self.cache_prefix, url_hash)

    def cache_set(self, url: str, resp: HttpResponse):
        """
        Save http response in cache.
        """
        self.cache.set(self.cache_build_key(url), pickle.dumps(resp), timeout=self.cache_timeout)

    def cache_retrieve(self, url: str) -> Optional[HttpResponse]:
        """
        Retrieve http response from cache.
        """
        resp = self.cache.get(self.cache_build_key(url))
        if resp is None:
            return None

        try:
            resp = pickle.loads(resp)
        except pickle.UnpicklingError as e:
            logger.error('Cannot unpickle rendered http response from cache: %s' % e, exc_info=True)
            return None

        if not isinstance(resp, HttpResponse):
            logger.error('Cached http response is not an instance of HttpResponse: %s' % type(resp))
            return None

        return resp

    def cache_clear(self, url: str):
        """
        Clear cached http response
        """
        self.cache.delete(self.cache_build_key(url))


class PrerenderIOHosted(RequestsDjangoResponseBuilderMixin, BackendBase):
    """
    Render with self-hosted version of prerender.io https://github.com/prerender/prerender
    """

    def __init__(
        self,
        *,
        render_url: str = '',
        update_url: str = '',
        session: SessionCreator = requests.Session,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.render_url = render_url or settings.PRERENDER_IO_HOSTED_URL
        if not self.render_url:
            raise ValueError('Render url is missing or empty')

        self.update_url = update_url or settings.PRERENDER_IO_HOSTED_UPDATE_URL
        if not self.update_url:
            raise ValueError('Update url is missing or empty')

        self.session = session()

    def render(self, url: str) -> HttpResponse:
        r = self.session.get('%s%s' % (self.render_url, url), allow_redirects=False)
        assert r.status_code < 500
        return self.requests_response_to_django_response(r)

    def update(self, url: str) -> bool:
        headers = {'Content-Type': 'application/json'}
        data = {'url': url}
        return self.session.post(self.update_url, json=data, headers=headers).status_code < 500


class PrerenderIO(PrerenderIOHosted):
    """
    Render with prerender.io
    """

    PRERENDER_IO_URL = 'https://service.prerender.io/'
    PRERENDER_IO_UPDATE_URL = 'https://api.prerender.io/recache'
    PRERENDER_TOKEN_HEADER_NAME = 'X-Prerender-Token'

    def __init__(
        self,
        *,
        token: str = '',
        **kwargs
    ):
        super().__init__(
            render_url=kwargs.pop('render_url', self.PRERENDER_IO_URL),
            update_url=kwargs.pop('update_url', self.PRERENDER_IO_UPDATE_URL),
            **kwargs,
        )

        self.token = token or settings.PRERENDER_IO_TOKEN
        if not self.token:
            raise ValueError('prerender.io token is missing or empty')
        self.session.headers[self.PRERENDER_TOKEN_HEADER_NAME] = self.token

    def update(self, url: str) -> bool:
        headers = {'Content-Type': 'application/json'}
        data = {'prerenderToken': self.token, 'url': url}
        return self.session.post(self.update_url, json=data, headers=headers).status_code < 500
