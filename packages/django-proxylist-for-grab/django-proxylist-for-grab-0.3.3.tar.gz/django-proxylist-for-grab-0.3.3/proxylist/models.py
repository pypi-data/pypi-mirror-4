# -*- coding: utf-8 -*-

import socket
import random
import json
import os

from dateutil.parser import parse
from datetime import timedelta
from random import randint
from pygeoip import GeoIP
from grab import Grab

from django_countries import CountryField
from django.core.cache import cache
from django.db import models

from proxylist.defaults import PROXY_LIST_MAX_CHECK_INTERVAL as max_check
from proxylist import now
import defaults


ANONYMITY_NONE = 0
ANONYMITY_LOW = 1
ANONYMITY_MEDIUM = 2
ANONYMITY_HIGH = 3


class ProxyCheckResult(models.Model):
    """The result of a proxy check"""

    mirror = models.ForeignKey('Mirror')

    proxy = models.ForeignKey('Proxy')

    #: Our real outbound IP Address (from worker)
    real_ip_address = models.IPAddressField(blank=True, null=True)

    #: Proxy outbound IP Address (received from mirror)
    hostname = models.CharField(max_length=25, blank=True, null=True)

    #: True if we found proxy related http headers
    forwarded = models.BooleanField(default=True)

    #: True if `real_ip_address` was found at any field
    ip_reveal = models.BooleanField(default=True)

    #: Check starts
    check_start = models.DateTimeField()

    #: Request was received at mirror server
    response_start = models.DateTimeField()

    #: Request was send back from the mirror
    response_end = models.DateTimeField()

    #: Check ends
    check_end = models.DateTimeField()

    raw_response = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(ProxyCheckResult, self).__init__(*args, **kwargs)
        if self.real_ip_address is None:
            self.real_ip_address = self._get_real_ip()

    def __unicode__(self):
        return str(self.check_start)

    def _get_real_ip(self):
        ip_key = '%s.%s.ip' % (socket.gethostname(), os.getpid())
        ip = cache.get(ip_key)
        if ip:
            return ip

        g = Grab(
            hammer_mode=True,
            hammer_timeouts=defaults.GRABBER_HAMMER_TIMEOUTS,
            connect_timeout=15,
            timeout=30
        )
        g.go("http://ifconfig.me/ip")
        ip = g.response.body.strip()

        cache.set(ip_key, ip, defaults.PROXY_LIST_OUTIP_INTERVAL)
        return ip

    def anonymity(self):
        if self.forwarded and self.ip_reveal:
            return ANONYMITY_NONE
        elif not self.forwarded and self.ip_reveal:
            return ANONYMITY_LOW
        elif self.forwarded and not self.ip_reveal:
            return ANONYMITY_MEDIUM
        else:
            return ANONYMITY_HIGH


class Mirror(models.Model):
    """A proxy checker site like.
    Ex: http://ifconfig.me/all.json
    """
    url = models.URLField(help_text='For example: http://local.com/mirror')

    output_type = models.CharField(
        max_length=10, default='plm_v1', choices=(
            ('plm_v1', 'ProxyList Mirror v1.0'),
        )
    )

    def __unicode__(self):
        return self.url

    def _make_request(self, proxy):
        """
        Make request to the mirror proxy
        """
        auth = None
        if proxy.user and proxy.password:
            auth = '%s:%s' % (proxy.user, proxy.password)

        g = Grab()
        g.setup(
            connect_timeout=defaults.PROXY_LIST_CONNECTION_TIMEOUT,
            timeout=defaults.PROXY_LIST_CONNECTION_TIMEOUT,
            proxy='%s:%d' % (proxy.hostname, proxy.port),
            proxy_type=proxy.proxy_type,
            proxy_userpwd=auth,
            user_agent=defaults.PROXY_LIST_USER_AGENT,
            hammer_mode=False,
        )
        g.go(str(self.url))
        return g.response

    def _parse_plm_v1(self, res, raw_data):
        """ Parse data from a ProxyList Mirror v1.0 output and fill a
        ProxyCheckResult object """

        FORWARD_HEADERS = [
            'FORWARDED',
            'X_FORWARDED_FOR',
            'X_FORWARDED_BY',
            'X_FORWARDED_HOST',
            'X_FORWARDED_PROTO',
            'VIA',
            'CUDA_CLIIP',
        ]
        FORWARD_HEADERS = set(FORWARD_HEADERS)

        data = json.loads(raw_data)

        res.response_start = parse(data['response_start'])
        res.response_end = parse(data['response_end'])

        res.hostname = data.get('REMOTE_ADDR', None)

        # True if we found proxy related http headers
        headers_keys = data['http_headers'].keys()
        res.forwarded = bool(FORWARD_HEADERS.intersection(headers_keys))

        headers_values = data['http_headers'].values()

        #: True if `real_ip_address` was found at any field
        res.ip_reveal = any(
            [x.find(res.real_ip_address) != -1 for x in headers_values])

    def is_checking(self, proxy):
        return bool(cache.get("proxy.%s.check" % proxy.pk))

    def _get_elapsed_time(self, proxy):
        time = []
        for i in range(random.choice(range(3, 15))):
            try:
                time.append(self._make_request(proxy).time)
            except:
                pass
        return sum(time) / float(len(time))

    def _check(self, proxy):
        """Do a proxy check"""

        check_key = "proxy.%s.check" % proxy.pk

        try:
            res = ProxyCheckResult()
            res.proxy = proxy
            res.mirror = self
            res.check_start = now()
            response = self._make_request(proxy)
            raw_data = response.body
            try:
                elapsed_time = '%1.2f' % self._get_elapsed_time(proxy)
            except:
                elapsed_time = response.time
            res.check_end = now()
            res.raw_response = raw_data

            if self.output_type == 'plm_v1':
                self._parse_plm_v1(res, raw_data)
            else:
                raise Exception('Output type not found!')

            proxy.update_from_check(res, elapsed_time)

            res.save()

            return res
        except:
            proxy.update_from_error()
            raise
        finally:
            # Task unlock
            cache.delete(check_key)

    def check(self, proxy):
        if defaults.PROXY_LIST_USE_CELERY:
            from proxylist.tasks import async_check

            check_key = "proxy.%s.check" % proxy.pk

            if self.is_checking(proxy):
                return None
            else:
                # Task lock
                cache.add(check_key, "true", defaults.PROXY_LIST_CACHE_TIMEOUT)

            return async_check.apply_async((proxy, self))
        return self._check(proxy)


class Proxy(models.Model):
    """A proxy server"""

    _geoip = GeoIP(defaults.PROXY_LIST_GEOIP_PATH)

    proxy_type_choices = (
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    )

    anonymity_level_choices = (
        # Anonymity can't be determined
        (None, 'Unknown'),

        # No anonymity; remote host knows your IP and knows you are using
        # proxy.
        (ANONYMITY_NONE, 'None'),

        # Low anonymity; proxy sent our IP to remote host, but it was sent in
        # non standard way (unknown header).
        (ANONYMITY_LOW, 'Low'),

        # Medium anonymity; remote host knows you are using proxy, but it does
        # not know your IP
        (ANONYMITY_MEDIUM, 'Medium'),

        # High anonymity; remote host does not know your IP and has no direct
        # proof of proxy usage (proxy-connection family header strings).
        (ANONYMITY_HIGH, 'High'),
    )

    hostname = models.CharField(max_length=75, unique=True)
    port = models.PositiveIntegerField()
    user = models.CharField(blank=True, null=True, max_length=50)
    password = models.CharField(blank=True, null=True, max_length=50)

    country = CountryField(blank=True, editable=False)

    proxy_type = models.CharField(
        default='http', max_length=10, choices=proxy_type_choices)

    anonymity_level = models.PositiveIntegerField(
        null=True, default=ANONYMITY_NONE, choices=anonymity_level_choices,
        editable=False)

    last_check = models.DateTimeField(null=True, blank=True, editable=False)

    next_check = models.DateTimeField(null=True, blank=True)

    created = models.DateTimeField(
        auto_now=False, auto_now_add=True, db_index=True, editable=False)

    errors = models.PositiveIntegerField(default=0, editable=False)

    elapsed_time = models.FloatField(blank=True, null=True, editable=False)

    def _update_next_check(self):
        """ Calculate and set next check time """

        delay = randint(defaults.PROXY_LIST_MIN_CHECK_INTERVAL,
                        defaults.PROXY_LIST_MAX_CHECK_INTERVAL)

        delay += defaults.PROXY_LIST_ERROR_DELAY * self.errors

        if self.last_check:
            self.next_check = self.last_check + timedelta(seconds=delay)
        else:
            self.next_check = now() + timedelta(seconds=delay)

    def update_from_check(self, check, elapsed_time):
        """ Update data from a ProxyCheckResult """

        if check.check_start:
            self.last_check = check.check_start
        else:
            self.last_check = now()
        self.errors = 0
        self.anonymity_level = check.anonymity()
        self._update_next_check()
        self.elapsed_time = elapsed_time
        self.save()

    def update_from_error(self):
        """ Last check was an error """

        self.last_check = now()
        self.errors += 1
        self._update_next_check()
        self.save()

    def save(self, *args, **kwargs):
        if not self.country:
            if self.hostname.count('.') == 3:
                self.country = self._geoip.country_code_by_addr(str(
                    self.hostname
                ))
            else:
                self.country = self._geoip.country_code_by_name(str(
                    self.hostname
                ))

        if not self.next_check:
            self.next_check = (now() - timedelta(seconds=max_check))

        super(Proxy, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Proxy'
        verbose_name_plural = 'Proxies'
        ordering = ('-last_check',)

    def __unicode__(self):
        return "%s://%s:%s" % (self.proxy_type, self.hostname, self.port)
