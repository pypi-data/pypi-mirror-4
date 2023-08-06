# -*- coding: utf-8 -*-

import os

import grab

import defaults
import models


APP_ROOT = os.path.normpath(os.path.dirname(__file__))
USER_AGENT_FILE = os.path.join(APP_ROOT, 'data/agents.txt')


def get_proxies():
    proxies = []
    for obj in models.Proxy.objects.filter(errors=0):
        proxy = '%s:%d' % (obj.hostname, obj.port)
        if obj.user and obj.password:
            proxy += ':%s:%s' % (obj.user, obj.password)
        proxies.append(proxy)
    return proxies


def Grab(**kwargs):
    grb = grab.Grab()
    default_settings = {
        'user_agent_file': USER_AGENT_FILE,
        'connect_timeout': defaults.GRABBER_CONNECT_TIMEOUT,
        'timeout': defaults.GRABBER_TIMEOUT,
        'hammer_mode': True,
        'hammer_timeouts': defaults.GRABBER_HAMMER_TIMEOUTS,
        'headers': defaults.GRABBER_HEADERS
    }
    default_settings.update(kwargs)
    grb.setup(**default_settings)
    grb.load_proxylist(
        source=get_proxies(),
        source_type='list',
        auto_init=True,
        auto_change=True
    )
    return grb
