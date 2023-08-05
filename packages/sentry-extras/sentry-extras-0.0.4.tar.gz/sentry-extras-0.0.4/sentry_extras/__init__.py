"""
sentry_extras
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2012 by David Szotten.
:license: MIT, see LICENSE for more details.
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('sentry-extras').version
except Exception, e:
    VERSION = 'unknown'
