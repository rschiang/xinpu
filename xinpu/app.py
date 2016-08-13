#!/usr/bin/env python
from .crawler import FeedCrawler
from .models import Config, Feed
from .poster import ContentPoster
from . import utils
import json
import logging
import threading

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
        return not self.terminating.wait(self.config.throttle)

    def post_item(self, item):
        self.poster.queue.put(item)

    def save_last_update(self):
        entity = {
            'last_updated': self.config.last_updated.isoformat(),
            'feeds': { feed.name: feed.last_updated.isoformat() for feed in self.config.feeds }
        }

        # Write to external file
        with open('last_updated.json', 'w') as f:
            json.dump(entity, f, ensure_ascii=False, indent='\t')

    @staticmethod
    def load_last_update(config):
        try:
            with open('last_updated.json', 'r') as f:
                entity = json.load(f)

            # Parse dates and stuff them to entity
            config['last_updated'] = utils.parse_date(entity['last_updated'])

            dates = { name: utils.parse_date(date_str) for name, date_str in entity['feeds'] }
            for feed in entity['feeds']:
                name = feed['name']
                if name in dates:
                    feed['last_updated'] = dates[name]

        except FileNotFoundError:
            logging.warning('last_updated file not present')
        except:
            logging.exception('Error while parsing last_updated file')

    @staticmethod
    def initialize():
        logging.info('Starting up Xinpu...')

        # Load configuration
        with open('config.json', 'r') as f:
            entity = json.load(f)

        # Try loading last update time from file
        Application.load_last_update(entity)

        return Application(config=Config(**entity))
