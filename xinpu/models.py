import peewee as p
from datetime import timedelta
from . import utils
import logging

# Generic class

class Config(object):
    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.lang = kwargs.get('lang', 'tr_ch')
        self.format = kwargs.get('format', '({site}) {url} ({title}): {summary}')
        self.throttle = kwargs.get('throttle', 5)
        self.backtrack = kwargs.get('backtrack', 0)
        self.feeds = []
        for feed in kwargs.get('feeds') or []:
            self.feeds.append(Feed(self, **feed))

class Feed(object):
    def __init__(self, config, **kwargs):
        self.name = kwargs.get('name')
        self.url = kwargs.get('url')
        self.interval = kwargs.get('interval', 0)
        self.options = kwargs.get('options', {})

        # Load model from database or create default ones
        try:
            model = FeedSource.get(FeedSource.name == self.name)
            self._last_updated = utils.parse_date(model.last_updated)
            self._last_checked = utils.parse_date(model.last_checked)
        except FeedSource.DoesNotExist:
            self._last_updated = (utils.local_now() - timedelta(seconds=config.backtrack))
            self._last_checked = self._last_updated - timedelta(seconds=self.interval)
            model = FeedSource(name=self.name, last_updated=self._last_updated, last_checked=self._last_checked)
        self._model = model

    def needs_update(self):
        return (utils.local_now() - self._last_checked).total_seconds() >= self.interval

    # Properties
    @property
    def last_updated(self):
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value):
        self._last_updated = value
        self._model.last_updated = value
        self._model.save()

    @property
    def last_checked(self):
        return self._last_checked

    @last_checked.setter
    def last_checked(self, value):
        self._last_checked = value
        self._model.last_checked = value
        self._model.save()


# Database entities
db = p.SqliteDatabase(None)

class BaseModel(p.Model):
    class Meta:
        database = db

class Item(BaseModel):
    site = p.CharField()
    title = p.CharField()
    url = p.CharField()
    image = p.CharField()
    summary = p.TextField()
    date = p.DateTimeField(default=utils.local_now)
    posted = p.BooleanField(default=False)

class FeedSource(BaseModel):
    name = p.CharField(max_length=31)
    last_updated = p.DateTimeField()
    last_checked = p.DateTimeField()
