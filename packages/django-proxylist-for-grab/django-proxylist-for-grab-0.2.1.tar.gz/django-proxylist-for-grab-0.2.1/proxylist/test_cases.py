# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from grab.error import GrabTimeoutError

from proxylist import grabber
from proxylist import models


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

    def __add_proxies(self):
        for data in self.proxies:
            self.proxy.create(**data)
        self.assertEqual(self.proxy.all().count(), 2)

    def __add_mirror(self):
        self.mirror.create(url=self.mirror_url)
        self.assertEqual(self.mirror.all().count(), 1)

    def test_a_settings_is_set(self):
        self.assertRaises(ObjectDoesNotExist, grabber.get_proxies)

    def test_b_setup_mirror(self):
        self.__add_mirror()

    def test_c_setup_proxies(self):
        self.__add_proxies()

    def test_d_send_message(self):
        self.__add_mirror()
        self.__add_proxies()

        proxy = lambda port: self.proxy.get(port=port)
        check = lambda proxy: self.mirror.get(pk=1).check(proxy)

        # OK
        check(proxy(7000))
        self.assertEqual(self.logs.all().count(), 1)
        self.assertEqual(self.logs.get(pk=1).ip_reveal, False)

        # ERROR
        self.assertRaises(GrabTimeoutError, check, proxy(3128))
        self.assertEqual(self.logs.all().count(), 1)
