# -*- coding: utf-8 -*-

from django.conf import settings


def get_settings(key, default):
    return getattr(settings, key, default)


PROXY_LIST_CACHE_TIMEOUT = get_settings(
    "PROXY_LIST_CACHE_TIMEOUT", 0)
PROXY_LIST_CONNECTION_TIMEOUT = get_settings(
    "PROXY_LIST_CONNECTION_TIMEOUT", 30)
PROXY_LIST_ERROR_DELAY = get_settings(
    "PROXY_LIST_ERRORDELAY", 300)
PROXY_LIST_GEOIP_PATH = get_settings(
    "PROXY_LIST_GEOIP_PATH", "/usr/share/GeoIP/GeoIP.dat")
PROXY_LIST_MAX_CHECK_INTERVAL = get_settings(
    "PROXY_LIST_MAX_CHECK_INTERVAL", 900)
PROXY_LIST_MIN_CHECK_INTERVAL = get_settings(
    "PROXY_LIST_MIN_CHECK_INTERVAL", 300)
PROXY_LIST_OUTIP_INTERVAL = get_settings(
    "PROXY_LIST_OUTIP_INTERVAL", 300)
PROXY_LIST_USER_AGENT = get_settings(
    "PROXY_LIST_USER_AGENT", "Django-Proxy 1.0.0")
PROXY_LIST_USE_CALLERY = get_settings(
    "PROXY_LIST_USE_CALLERY", False)

GRABBER_HEADERS = get_settings(
    'GRABBER_HEADERS', {'Accept-Language': 'ru-ru,ru;q=0.7'})
GRABBER_HAMMER_TIMEOUTS = get_settings(
    'GRABBER_HAMMER_TIMEOUTS', ((60, 70), (80, 90), (100, 110)))
GRABBER_TIMEOUT = get_settings('GRABBER_TIMEOUT', 60)
GRABBER_CONNECT_TIMEOUT = get_settings('GRABBER_CONNECT_TIMEOUT', 2)
