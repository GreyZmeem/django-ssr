from typing import Callable, Union

from django.http import HttpResponse, HttpRequest
from django.utils.decorators import decorator_from_middleware_with_args
from django.utils.module_loading import import_string

from django_ssr import backends, helpers, settings

Backend = Union[str, Callable[..., backends.BackendBase]]
GetResponse = Callable[[HttpRequest], HttpResponse]


class BaseMiddleware:
    """
    Base class for SSR's middleware
    """

    def __init__(
        self,
        get_response: GetResponse,
        backend: Backend = None
    ):
        self.get_response = get_response

        backend = backend if backend is not None else settings.BACKEND
        if isinstance(backend, str):
            backend = import_string(backend)
        self.backend = backend()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if self.must_render(request):
            return self.backend.render(self.backend.build_absolute_url(request))
        return self.get_response(request)

    def must_render(self, request: HttpRequest) -> bool:
        """
        Return `True` if request must be rendered by backend.
        """
        raise NotImplementedError('%s.must_render is not implemented' % self.__class__.__name__)


class UserAgentMiddleware(BaseMiddleware):
    """
    Render page if request's User-Agent matches `settings.DJANGO_SSR_USER_AGENTS`
    """

    def must_render(self, request: HttpRequest) -> bool:
        ua = request.META.get('HTTP_USER_AGENT', '')
        url = self.backend.build_absolute_url(request)
        return helpers.is_user_agent_match(ua) and helpers.must_render(url)


user_agent_ssr = decorator_from_middleware_with_args(UserAgentMiddleware)
