#!/usr/bin/env python
"""
sentry-extras.filters
===============

Some useful extras for [Sentry](https://getsentry.com)

:copyright: (c) 2012 by David Szotten.
:license: MIT, see LICENSE for more details.
"""

from django.utils.datastructures import SortedDict
from sentry.conf import settings
from sentry.filters import SentryFilter


class LevelAndAboveFilter(SentryFilter):
    label = 'Level (and above)'
    column = 'level'
    query_param = 'level_and'

    def get_choices(self):
        return SortedDict((str(k), v) for k, v in settings.LOG_LEVELS)

    def get_query_set(self, queryset):
        return queryset.filter(level__gte=self.get_value())
