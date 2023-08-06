# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='django-proxylist-for-grab',
    version="0.3.0",
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
    author="GoTLiuM InSPiRiT",
    author_email='gotlium@gmail.com',
    url='https://github.com/gotlium/django-proxylist',
    license='GPL',
    packages=find_packages(),
    package_data={'proxylist': [
        'data/agents.txt',
    ]},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django-countries',
        'python-dateutil',
        'pygeoip',
        'django',
        'pycurl',
        'grab',
    ]
)
