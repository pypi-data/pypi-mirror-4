# -*- coding: utf-8 -*-

import os

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from grab.error import GrabTimeoutError

from proxylist import grabber
from proxylist import models

from proxylist import now
import defaults


class ProxyListTestCase(TestCase):
    def setUp(self):
        self.proxies = [
            {
                'user': 'proxylist',
                'password': '1f3a3b28c1a0cc3f',
                'hostname': 'fastun.ru',
                'port': 7000,
            },
            {
                'hostname': '7.7.7.7',
                'port': 3128,
            }
        ]
        self.mirror_url = 'http://live-film.net/mirror'
        self.proxy = models.Proxy.objects
        self.mirror = models.Mirror.objects
        self.logs = models.ProxyCheckResult.objects

    def _add_proxies(self, port=None, count=0):
        for data in self.proxies:
            if port and data['port'] != port:
                continue
            data['last_check'] = now()
            self.proxy.create(**data)
            count += 1
        self.assertEqual(self.proxy.all().count(), count)

    def _add_mirror(self):
        self.mirror.create(url=self.mirror_url)
        self.assertEqual(self.mirror.all().count(), 1)

    def _check_grab(self, grab):
        self.assertEqual(grab.config.get('proxy').split(':')[-1], '7000')
        self.assertEqual(':7000' in grab.config.get('proxy'), True)
        self.assertEqual(grab.response.code, 200)
        # self.assertEqual(grab.doc.select('//html/body').exists(), True)
        self.assertEqual(grab.xpath_exists('//html/body'), True)

    def test_a_settings_is_set(self):
        self.assertRaises(ObjectDoesNotExist, grabber.get_proxies)

    def test_b_setup_mirror(self):
        self._add_mirror()

    def test_c_setup_proxies(self):
        self._add_proxies()

    def test_d_check_proxies(self):
        self._add_mirror()
        self._add_proxies()

        proxy = lambda port: self.proxy.get(port=port)
        check = lambda proxy: self.mirror.get(pk=1).check(proxy)

        # OK
        check(proxy(7000))
        self.assertEqual(self.logs.all().count(), 1)
        self.assertEqual(self.logs.get(pk=1).ip_reveal, False)

        # ERROR
        self.assertRaises(GrabTimeoutError, check, proxy(3128))
        self.assertEqual(self.logs.all().count(), 1)

    def test_e_settings(self, **kwargs):
        self.assertEqual(defaults.GRABBER_CONNECT_TIMEOUT, 5)
        self.assertEqual(defaults.GRABBER_TIMEOUT, 5)

    def test_f_grab(self):
        from proxylist import grabber

        self._add_mirror()
        self._add_proxies(7000)

        self.assertEqual(os.path.isdir(grabber.APP_ROOT), True)
        self.assertEqual(os.path.exists(grabber.USER_AGENT_FILE), True)

        self.assertEqual(len(grabber.get_proxies()), 1)
        self.assertEqual('proxylist' in grabber.get_proxies()[0], True)

        grab = grabber.Grab()
        grab.go('http://www.google.com/')
        self._check_grab(grab)

    def test_g_spider(self):
        from grab.spider.base import Task
        from proxylist.grabber import Spider

        self._add_mirror()
        self._add_proxies(7000)

        base = self

        class SimpleSpider(Spider):
            initial_urls = ['http://ya.ru/']

            def task_initial(self, grab, task):
                grab.set_input('text', 'linux')
                grab.submit(make_request=False)
                yield Task('search', grab=grab)

            def task_search(self, grab, task):
                base._check_grab(grab)

        bot = SimpleSpider()
        bot.run()
