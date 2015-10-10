from datetime import datetime, timedelta

class Config(object):
    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.format = kwargs.get('format', '({site}) {url} ({title}): {summary}')
        self.throttle = kwargs.get('throttle', 5)
        self.backtrack = kwargs.get('backtrack', 0)
        self.last_updated = kwargs.get('last_updated') or (datetime.now() - timedelta(seconds=self.backtrack))
        self.feeds = []
        for feed in kwargs.get('feeds') or []:
            self.feeds.append(Feed(**feed))

class Feed(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.url = kwargs.get('url')
        self.interval = kwargs.get('interval', 0)
        self.options = kwargs.get('options', {})
        self.last_updated = config.last_updated

    def needs_update(self):
        return (datetime.now() - self.last_updated).total_seconds() >= self.interval