#!/usr/bin/env python
from datetime import datetime, timedelta
import json
import threading
import trace
import sys

'''
Event to inform threads to stop.
'''
app = threading.Event()
config = {}

class Site(object):
    def __init__(self, name=None, url=None, interval=None, options=None):
        self.name = name
        self.url = url
        self.interval = interval or 0
        self.options = options or {}
        self.last_updated = config['last_updated'] or (datetime.now() - timedelta(seconds=config['backtrack']))

    def needs_update(self):
        return (datetime.now() - self.last_updated).total_seconds() >= self.interval

class FeedCrawler(threading.Thread):
    def __init__(self):
        super(FeedCrawler, self).__init__(name='crawler')
        self.daemon = True

    def run(self):
        while app.wait(timeout=)

class ContentPoster(threading.Thread):
    def __init__(self):
        super(ContentPoster, self).__init__(name='poster')
        self.daemon = True

def launch():
    trace.info('starting up.')
    try:
        # Read settings file
        configure()

        # Launch threads
        crawler = FeedCrawler()
        poster = ContentPoster()

        # Block until any key pressed
        sys.stdin.read()
    finally:
        trace.info('shutting down.')
        app.set()

def configure():
    with open('config.json', 'r') as f:
        # Set some important defaults
        entity = {
            'format': '({site}) {url} ({title}): {summary}',
            'throttle': 5,
            'backtrack': 0,
        }

        # Read configuration from file
        entity.update(json.load(f))

        # Load sites
        sites = []
        for site in entity['feeds']:
            sites.append(Site(**site))
        entity['sites'] = sites

        # Save to global configuration
        global config = entity

if __name__ == '__main__':
    threading.current_thread().name = 'main'
    launch()
