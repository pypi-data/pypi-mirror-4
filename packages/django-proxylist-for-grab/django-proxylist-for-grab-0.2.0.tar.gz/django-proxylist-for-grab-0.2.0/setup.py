# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='django-proxylist-for-grab',
    version="0.2.0",
    description='Proxy-list management application for Django',
    keywords='django proxylist grab',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: Proxy Servers',
    ],
    author='Roberto Abdelkader Mart\xc3\xadnez P\xc3\xa9rez',
    author_email='robertomartinezp@gmail.com',
    url='https://github.com/gotlium/django-proxylist',
    license='GPL',
    packages=find_packages(),
    package_data={'proxylist': [
        'data/agents.txt',
        'management/commands/*'
    ]},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-countries',
        'pygeoip',
        'django-celery',
        'django',
        'grab',
    ]
)
