from datetime import timedelta
from . import utils

class Config(object):
    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.lang = kwargs.get('lang', 'tr_ch')
        self.format = kwargs.get('format', '({site}) {url} ({title}): {summary}')
        self.throttle = kwargs.get('throttle', 5)
        self.backtrack = kwargs.get('backtrack', 0)
        self.feeds = []
        for feed in kwargs.get('feeds') or []:
            self.feeds.append(Feed(config, **feed))

class Feed(object):
    def __init__(self, config, **kwargs):
        self.name = kwargs.get('name')
        self.url = kwargs.get('url')
        self.interval = kwargs.get('interval', 0)
        self.options = kwargs.get('options', {})
        self.last_updated = kwargs.get('last_updated') or (utils.local_now() - timedelta(seconds=config.backtrack))
        self.last_checked = self.last_updated - timedelta(seconds=self.interval)

    def needs_update(self):
        return (utils.local_now() - self.last_checked).total_seconds() >= self.interval
