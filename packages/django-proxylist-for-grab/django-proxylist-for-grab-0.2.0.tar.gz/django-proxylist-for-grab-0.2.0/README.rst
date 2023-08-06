Django-ProxyList-For-Grab
=========================

This application is useful for keep an updated list of proxy servers, it
contains everything you need to make periodic checks to verify the properties
of the proxies.



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
        print grab.doc.select('//div').number()


* Gihub: https://github.com/gotlium/django-proxylist
