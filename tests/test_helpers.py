import re

from django_ssr import helpers


def test_is_url_ignored():
    items = {re.compile(r'http://example\.com/test'), re.compile(r'http://example\.net/test')}
    assert helpers.is_url_ignored('http://example.com/test/url', items)
    assert helpers.is_url_ignored('http://example.net/test/url', items)
    assert not helpers.is_url_ignored('http://example.ua/test/url', items)


def test_is_path_ignored():
    items = {re.compile(r'/test')}
    assert helpers.is_path_ignored('http://example.com/test', items)
    assert helpers.is_path_ignored('http://example.com/test/url', items)
    assert not helpers.is_path_ignored('http://example.com/url/test', items)


def test_is_extension_ignored():
    items = {'.js', '.css'}
    assert helpers.is_extension_ignored('http://example.com/.js', items)
    assert helpers.is_extension_ignored('http://example.com/.js?', items)
    assert helpers.is_extension_ignored('http://example.com/min.js', items)
    assert helpers.is_extension_ignored('http://example.com/.css', items)
    assert helpers.is_extension_ignored('http://example.com/.css?', items)
    assert helpers.is_extension_ignored('http://example.com/min.css', items)
    assert not helpers.is_extension_ignored('http://example.com/js', items)
    assert not helpers.is_extension_ignored('http://example.com/css', items)


def test_user_agent_match():
    items = {re.compile('.*googlebot', re.I), re.compile('.*bingbot', re.I), re.compile('.*yandex', re.I)}
    assert helpers.is_user_agent_match('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', items)  # noqa
    assert helpers.is_user_agent_match('Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)', items)  # noqa
    assert helpers.is_user_agent_match('User-Agent Mozilla/5.0 (compatible; Yandex...)', items)
    assert not helpers.is_user_agent_match('Google-Bot', items)
    assert not helpers.is_user_agent_match('Bing-Bot', items)


def test_must_render():
    assert not helpers.must_render('http://example.com/')
    assert not helpers.must_render('http://example.net/media/')
    assert not helpers.must_render('http://example.net/static/')
    assert not helpers.must_render('http://example.net/app.css')
    assert not helpers.must_render('http://example.net/app.js')
    assert helpers.must_render('http://example.net/app')
    assert helpers.must_render('http://example.net/admin')
