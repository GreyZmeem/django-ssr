import datetime
import re
from typing import Container, Iterable, Pattern, Union

from django.conf import settings
from django.test.signals import setting_changed


def s(name: str):
    """
    Return value from django's settings or default
    """
    return getattr(settings, 'DJANGO_SSR_%s' % name, DEFAULTS[name])


DEFAULTS = {
    'ENABLED': not settings.DEBUG,
    'BACKEND': 'django_ssr.backends.PrerenderIO',
    'STRIP_QUERY_PARAMS': False,

    'CACHE_ALIAS': 'default',
    'CACHE_PREFIX': 'django-ssr',
    'CACHE_TIMEOUT': int(datetime.timedelta(days=14).total_seconds()),

    'IGNORE_EXTENSIONS': {
        '.js',
        '.css',
        '.jpg',
        '.jpeg',
        '.svg',
        '.gif',
        '.png',
        '.txt',
        '.xml',
        '.ico',
    },
    'IGNORE_PATH': {
        re.compile(r'/media/'),
        re.compile(r'/static/'),
    },
    'IGNORE_URLS': {
        re.compile(r'https?://example\.com/', re.I),
    },
    'REMOVE_HEADERS': {
        'connection',
        'keep-alive',
        'proxy-authenticate',
        'proxy-authorization',
        'te',
        'trailers',
        'transfer-encoding',
        'upgrade',
        'content-encoding',
    },
    'USER_AGENTS': {
        # Google crawlers: https://support.google.com/webmasters/answer/1061943?hl=en
        re.compile(r'.*Googlebot', re.I),
        re.compile(r'.*Mediapartners-Google', re.I),
        re.compile(r'.*AdsBot-Google', re.I),
    },

    # Self-hosted https://prerender.io
    'PRERENDER_IO_HOSTED_URL': '',
    'PRERENDER_IO_HOSTED_UPDATE_URL': '',

    # https://prerender.io
    'PRERENDER_IO_TOKEN': '',
}


ENABLED = s('ENABLED')  # type: bool
BACKEND = s('BACKEND')  # type: str
STRIP_QUERY_PARAMS = s('STRIP_QUERY_PARAMS')  # type: bool

CACHE_ALIAS = s('CACHE_ALIAS')  # type: str
CACHE_PREFIX = s('CACHE_PREFIX')  # type: str
CACHE_TIMEOUT = s('CACHE_TIMEOUT')  # type: int

IGNORE_EXTENSIONS = s('IGNORE_EXTENSIONS')  # type: Iterable
IGNORE_PATH = s('IGNORE_PATH')  # type: Iterable[Pattern]
IGNORE_URLS = s('IGNORE_URLS')  # type: Iterable[Pattern]
REMOVE_HEADERS = s('REMOVE_HEADERS')  # type: Union[Container, Iterable]
USER_AGENTS = s('USER_AGENTS')  # type: Iterable[Pattern]

# Self-hosted https://prerender.io
PRERENDER_IO_HOSTED_URL = s('PRERENDER_IO_HOSTED_URL')  # type: str
PRERENDER_IO_HOSTED_UPDATE_URL = s('PRERENDER_IO_HOSTED_UPDATE_URL')  # type: str

# https://prerender.io
PRERENDER_IO_TOKEN = s('PRERENDER_IO_TOKEN')  # type: str


def reload_settings(*args, **kwargs):
    name, val = kwargs['setting'].replace('DJANGO_SSR_', ''), kwargs['value']
    if name not in DEFAULTS:
        return
    val = val if val is not None else s(name)
    globals()[name] = val


setting_changed.connect(reload_settings)
