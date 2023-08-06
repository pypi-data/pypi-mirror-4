# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from proxylist.models import Proxy


class Command(BaseCommand):
    help = 'Remove broken proxies.'

    def handle(self, *args, **options):
        Proxy.objects.filter(errors__gt=0).delete()
