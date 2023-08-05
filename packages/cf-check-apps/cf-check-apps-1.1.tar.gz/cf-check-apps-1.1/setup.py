#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


INSTALL_REQUIRES = [
    'gevent',
    'grequests',
    'requests',
    'docopt',
]


setup(
    name='cf-check-apps',
    version='1.1',
    description='Check the status of your CloudFoundry apps',
    author='Jonas Obrist',
    author_email='ojiidotch@gmail.com',
    url='https://github.com/ojii/cf-check-apps',
    install_requires=INSTALL_REQUIRES,
    license='BSD',
    platforms=['OS Independent'],
    scripts=['cf_check_apps.py'],
    long_description='Check the status of your CloudFoundry apps',
    include_package_data=True,
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'cf-check-apps = cf_check_apps:cli',
        ],
    },
)
