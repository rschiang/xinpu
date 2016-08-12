#!/usr/bin/env python
from queue import Queue
from .crawler import FeedCrawler
from .models import Config, Feed
from .poster import ContentPoster
import dateutil
import json
import logging
import threading
import sys

class Application(object):
    def __init__(self, config=None):
        self.terminating = threading.Event()
        self.config = config
        self.crawler = FeedCrawler(app=self)
        self.poster = ContentPoster(app=self)

    def start(self):
        self.crawler.start()
        self.poster.start()

    def stop(self):
        logging.info('Shutting down Xinpu...')
        self.terminating.set()

    def running(self):
        return not self.terminating.wait(config.throttle)

    def post_item(self, item):
        self.poster.queue.put(item)

    def load_last_update(self):
        try:
            with open('last_updated.txt', 'r') as f:
                date_str = f.read().strip()
                last_updated = dateutil.parser.parse(date_str)
                return last_updated
        except:
            logging.exception('Error while parsing last_updated file')
            return None

    def set_last_update(self, date):
        self.config.last_updated = date
        with open('last_updated.txt', 'w') as f:
            f.write(self.config.last_updated.isoformat())

    @staticmethod
    def initialize():
        logging.info('Starting up Xinpu...')

        # Load configuration
        with open('config.json', 'r') as f:
            entity = json.load(f)

        # Try loading last update time from file
        entity['last_updated'] = load_last_update()

        return Application(config=Config(**entity))


if __name__ == '__main__':  # Running from console
    app = Application.initialize()
    app.start()
    try:
        sys.stdin.read()    # Block until any key pressed
    finally:
        app.stop()          # Gracefully stop the application
