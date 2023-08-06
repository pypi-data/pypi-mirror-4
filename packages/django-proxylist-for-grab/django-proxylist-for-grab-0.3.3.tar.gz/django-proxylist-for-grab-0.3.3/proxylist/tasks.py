# -*- coding: utf-8 -*-

from celery.task import Task
from celery import task

from management.commands.check_proxies import check_proxies
from management.commands.clean_proxies import clean_proxies
from management.commands.grab_proxies import grab_proxies


@task(ignore_result=True)
def async_check(proxy, checker):
    try:
        checker._check(proxy)
    except:
        pass


class CleanProxies(Task):
    def run(self, *args, **kwargs):
        clean_proxies()


class GrabProxies(Task):
    ignore_result = True
    send_error_emails = False

    def run(self, *args, **kwargs):
        grab_proxies()


class CheckProxies(Task):
    def run(self, *args, **kwargs):
        check_proxies()
