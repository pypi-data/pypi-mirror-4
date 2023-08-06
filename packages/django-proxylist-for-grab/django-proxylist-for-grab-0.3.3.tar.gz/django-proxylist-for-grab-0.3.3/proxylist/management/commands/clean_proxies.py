# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

import proxylist.defaults as defaults
from proxylist.models import Proxy


def clean_proxies():
    Proxy.objects.filter(errors__gt=0).delete()
    if defaults.PROXY_LIST_ELAPSED_TIME is not None:
        Proxy.objects.filter(
            elapsed_time__gt=defaults.PROXY_LIST_ELAPSED_TIME).delete()


class Command(BaseCommand):
    help = 'Remove broken proxies.'

    def handle(self, *args, **options):
        clean_proxies()
