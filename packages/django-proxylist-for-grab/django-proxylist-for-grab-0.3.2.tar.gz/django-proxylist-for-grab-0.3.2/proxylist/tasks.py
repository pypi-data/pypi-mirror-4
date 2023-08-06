# -*- coding: utf-8 -*-

from celery import task


@task(ignore_result=True)
def async_check(proxy, checker):
    try:
        checker._check(proxy)
    except:
        pass
