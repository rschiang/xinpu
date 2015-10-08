#!/usr/bin/env python
from queue import Queue
from .crawler import FeedCrawler
from .models import Config, Feed
from .poster import ContentPoster
import json
import threading
import trace
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
        trace.info('Shutting down Xinpu...')
        self.terminating.set()

    def running(self):
        return not self.terminating.wait(config.throttle)

    def post_item(self, item):
        self.poster.queue.put(item)

    @staticmethod
    def initialize():
        trace.info('Starting up Xinpu...')

        # Load configuration
        with open('config.json', 'r') as f:
            entity = json.load(f)

        return Application(config=Config(**entity))


if __name__ == '__main__':  # Running from console
    app = Application.initialize()
    app.start()
    try:
        sys.stdin.read()    # Block until any key pressed
    finally:
        app.stop()          # Gracefully stop the application
