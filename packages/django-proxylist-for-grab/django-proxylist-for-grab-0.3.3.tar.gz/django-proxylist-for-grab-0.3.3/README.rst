Django-ProxyList-For-Grab
=========================

.. image:: https://api.travis-ci.org/gotlium/django-proxylist.png?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/gotlium/django-proxylist

This application is useful for keep an updated list of proxy servers, it
contains everything you need to make periodic checks to verify the properties
of the proxies. Also you can periodically collect the proxy server
from the Internet, remove broken and slow proxies.



Installing the package
----------------------

`django-proxylist-for-grab` can be easily installed using pip:

.. code-block:: bash

   $ pip install django-proxylist-for-grab



Configuration
-------------

After that you need to include `django-proxylist-for-grab` into your
*INSTALLED_APPS* list of your django settings file.

.. code-block:: python

   INSTALLED_APPS = (
     ...
     'proxylist',
     ...
   )

Add `django-proxylist-for-grab` into ``urls.py``

.. code-block:: python

   urlpatterns = patterns(
    ...
    url(r'', include('proxylist.urls')),
    ...
   )


`django-proxylist-for-grab` has a list of variables that you can configure
throught django's settings file. You can see the entire list at
Advanced Configuration.



Database creation
-----------------

You have two choices here:

Using south
~~~~~~~~~~~

We ancourage recommend you using `south` for your database migrations. If you
already use it you can migrate `django-proxylist-for-grab`:

.. code-block:: bash

   $ python manage.py migrate proxylist



Using syncdb
~~~~~~~~~~~~

If you don't want to use `south` you can make a plain *syncdb*:

.. code-block:: bash

   $ python manage.py syncdb



Basic setup
-----------

At first, add a mirror. For working mirror, you need to install app on
server with external ip. This is in order to be able to verify the correctness
of data through proxy server. After adding mirror, you can add and test
your proxies.



Asynchronously checking
-----------------------
`django-proxylist-for-grab` has configured by default to non-async check.
You can change this behavior. Insert into your django settings
``PROXY_LIST_USE_CALLERY`` and change it to True.

After you need to install and configure django-celery and rabbit-mq.

For example on OS X
~~~~~~~~~~~~~~~~~~~
**Packages installation**

.. code-block:: bash

    $ sudo pip install django-celery
    $ sudo port install rabbitmq-server

Add the 'djcelery' application to 'INSTALLED_APPS' in settings

.. code-block:: python

   INSTALLED_APPS = (
     ...
     'djcelery',
     ...
   )

**Sync database**

.. code-block:: bash

    $ ./manage.py syncdb

**Run rabbitmq and celery**

.. code-block:: bash

    $ sudo rabbitmq-server -detached
    $ nohup python manage.py celery worker >& /dev/null &



Command line reference
----------------------

update_proxies
~~~~~~~~~~~~~~

Add new proxies from a file.

.. code-block:: bash

   $ python manage.py update_proxies [file1] <file2> <...>


check_proxies
~~~~~~~~~~~~~

Check proxies availability and anonymity.

.. code-block:: bash

   $ python manage.py check_proxies


grab_proxies
~~~~~~~~~~~~

Search proxy list on internet


.. code-block:: bash

   $ python manage.py grab_proxies


clean_proxies
~~~~~~~~~~~~~

Remove broken proxies


.. code-block:: bash

   $ python manage.py clean_proxies



GrabLib usage example:
----------------------

.. code-block:: python

    from proxylist import grabber

    grab = grabber.Grab()

    # Get your ip (You can do this a few times to see how the proxy will be changed)
    grab.go('http://ifconfig.me/ip')
    if grab.response.code == 200:
        print grab.response.body.strip()

    # Get count of div on google page
    grab.go('http://www.google.com/')
    if grab.response.code == 200:
        print len(grab.xpath_list('//div'))




GrabLib Spider example:
----------------------

.. code-block:: python

    # filename: apps/app/management/commands/spider.py
    # usage: python manage.py spider
    from django.core.management.base import BaseCommand
    from grab.spider.base import Task
    from proxylist.grabber import Spider


    class SimpleSpider(Spider):
        initial_urls = ['http://ya.ru/']

        def task_initial(self, grab, task):
            grab.set_input('text', 'linux')
            grab.submit(make_request=False)
            yield Task('search', grab=grab)

        def task_search(self, grab, task):
            for elem in grab.xpath_list('//h2/a'):
                print elem.text_content()


    class Command(BaseCommand):
        help = 'Simple Spider'

        def handle(self, *args, **options):
            bot = SimpleSpider()
            bot.run()
            print bot.render_stats()



* Gihub: https://github.com/gotlium/django-proxylist
