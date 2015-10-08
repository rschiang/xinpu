#!/usr/bin/env python
from datetime import datetime, timedelta
from queue import Queue
import json
import threading
import trace
import sys

'''
Event to inform threads to stop.
'''
app = threading.Event()
config = None

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
        self.options = kwargs.get('options')
        self.last_updated = config.last_updated

    def needs_update(self):
        return (datetime.now() - self.last_updated).total_seconds() >= self.interval

class FeedCrawler(threading.Thread):
    def __init__(self):
        super(FeedCrawler, self).__init__(name='crawler')
        self.daemon = True

    def run(self):
        while not app.wait(timeout=config.throttle):
            for feed in config.feeds:
                if not feed.needs_update():
                    continue
                # Fetch new feed

    def post_item(self, item):
        raise NotImplementedError('No event handler provided')

class ContentPoster(threading.Thread):
    def __init__(self):
        super(ContentPoster, self).__init__(name='poster')
        self.daemon = True
        self.queue = Queue()

    def run(self):
        while not app.wait(timeout=config.throttle):
            if self.queue.empty():
                continue

            item = self.queue.get()
            # Post item

def launch():
    trace.info('starting up.')
    try:
        # Read settings file
        configure()

        # Configure threads
        crawler = FeedCrawler()
        poster = ContentPoster()
        crawler.post_item = lambda item: poster.queue.put(item)

        # Launch threads
        crawler.start()
        poster.start()

        # Block until any key pressed
        sys.stdin.read()
    finally:
        trace.info('shutting down.')
        app.set()

def configure():
    with open('config.json', 'r') as f:
        # Read configuration from file
        entity = json.load(f)

        # Save to global configuration
        global config = Config(**entity)

if __name__ == '__main__':
    threading.current_thread().name = 'main'
    launch()
