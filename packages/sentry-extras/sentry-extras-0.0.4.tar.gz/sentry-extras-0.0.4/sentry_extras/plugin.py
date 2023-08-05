import sentry_extras
from sentry_extras.filters import LevelAndAboveFilter
from sentry.plugins import Plugin

class SentryExtras(Plugin):
    title = 'Sentry Extras'
    slug = 'sentry-extras'
    description = 'Some useful extras'
    version = sentry_extras.VERSION

    author = 'David Szotten'
    author_url = 'https://github.com/davidszotten/sentry_extras'

    def get_filters(self, project=None, **kwargs):
        return [LevelAndAboveFilter]
