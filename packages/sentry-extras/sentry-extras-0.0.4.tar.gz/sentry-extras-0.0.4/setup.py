#!/usr/bin/env python
"""
sentry-extras
===============

Some useful extras for [Sentry](https://getsentry.com)

:copyright: (c) 2012 by David Szotten.
:license: MIT, see LICENSE for more details.
"""
from setuptools import setup, find_packages


install_requires = [
    'sentry>=5.0.0',
]

setup(
    name='sentry-extras',
    version='0.0.4',
    author='David Szotten',
    author_email='Author name (as one word) at gmail.com',
    url='http://github.com/davidszotten/sentry-extras',
    description='Some useful extras for Sentry',
    long_description=__doc__,
    license='MIT',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
       'sentry.plugins': [
            'pluginname = sentry_extras.plugin:SentryExtras'
        ],
    },
)

