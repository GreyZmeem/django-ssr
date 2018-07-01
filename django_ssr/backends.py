from typing import Callable
from urllib.parse import urlparse, ParseResult

import requests
from django.http import HttpRequest, HttpResponse

from django_ssr import settings

__all__ = [
    'BackendBase',
    'PrerenderIOHosted',
    'PrerenderIO',
]

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
        return self.session.post(self.update_url, data, headers=headers).status_code < 500


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
