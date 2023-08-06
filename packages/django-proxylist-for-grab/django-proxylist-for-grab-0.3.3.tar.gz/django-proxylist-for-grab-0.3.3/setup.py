# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='django-proxylist-for-grab',
    version="0.3.3",
    description='Proxy-list management application for Django',
    keywords='django proxylist grab',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Proxy Servers',
    ],
    author="GoTLiuM InSPiRiT",
    author_email='gotlium@gmail.com',
    url='https://github.com/gotlium/django-proxylist',
    license='GPL v3',
    packages=find_packages(exclude=['demo']),
    package_data={'proxylist': [
        'data/agents.txt',
    ]},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-countries',
        'python-dateutil',
        'multiprocessing',
        'pygeoip',
        'django',
        'pycurl',
        'lxml',
        'grab == 0.4.8',
    ]
)
