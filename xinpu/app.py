#!/usr/bin/env python
from plurk_oauth import PlurkAPI
from . import models
import json
import logging
import os
import sys

API_KEY_PATH = os.environ.get('XINPU_API_KEY', 'plurk.json')
CONFIG_FILE_PATH = os.environ.get('XINPU_CONFIG', 'config.json')
DATABASE_PATH = os.environ.get('XINPU_DB', 'cache.db')
LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
IS_DRILL = os.environ.get('XINPU_DRILL')

class Application(object):
    def __init__(self, name='default'):
        self.name = name

        # Set up logging
        logging.basicConfig(stream=sys.stdout, format='[%(asctime)s][%(module)s] %(levelname)s: %(message)s', level=LOGLEVEL)
        logging.debug('%s starting up', self.name)

        # Set up database
        models.db.init(DATABASE_PATH)
        models.db.create_tables([models.Item, models.FeedSource])

        # Load configuration
        with open(CONFIG_FILE_PATH, 'r') as f:
            self.config = models.Config(**(json.load(f)))

        # Initialize shared services
        self.plurk = PlurkAPI.fromfile(API_KEY_PATH)
        self.is_drill = bool(IS_DRILL)

    def __del__(self):
        logging.debug('%s shutting down', self.name)
