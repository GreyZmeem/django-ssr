from typing import Iterable, Pattern
from urllib.parse import urlparse

from django_ssr import settings


def must_render(url: str) -> bool:
    """
    Check if url must be rendered.
    """
    return all([
        settings.ENABLED,
        not is_url_ignored(url),
        not is_path_ignored(url),
        not is_extension_ignored(url),
    ])


def is_url_ignored(url: str, ignored_urls: Iterable[Pattern] = None) -> bool:
    """
    Check url is in the list of ignored urls.
    """
    ignored_urls = ignored_urls if ignored_urls is not None else settings.IGNORE_URLS
    for r in ignored_urls:
        if r.match(url):
            return True
    return False


def is_path_ignored(url: str, ignored_path: Iterable[Pattern] = None) -> bool:
    """
    Check url's path is in the list of ignored paths.
    """
    ignored_path = ignored_path if ignored_path is not None else settings.IGNORE_PATH
    path = urlparse(url).path
    for r in ignored_path:
        if r.match(path):
            return True
    return False


def is_extension_ignored(url: str, ignored_ext: Iterable = None) -> bool:
    """
    Check url's file extension is in the list of ignored extensions.
    """
    ignored_ext = ignored_ext if ignored_ext is not None else settings.IGNORE_EXTENSIONS
    path = urlparse(url).path
    for ext in ignored_ext:
        if path.endswith(ext):
            return True
    return False


# @lru_cache(settings.USER_AGENT_MATCH_LRU_SIZE)
def is_user_agent_match(user_agent: str, user_agents: Iterable[Pattern] = None) -> bool:
    """
    Check user agent is the list.
    """
    user_agents = user_agents if user_agents is not None else settings.USER_AGENTS
    for r in user_agents:
        if r.match(user_agent):
            return True
    return False
