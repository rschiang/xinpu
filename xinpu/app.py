#!/usr/bin/env python
from plurk_oauth import PlurkAPI
from .models import Config, db
import json
import logging
import os

API_KEY_PATH = os.environ.get('XINPU_API_KEY', 'plurk.json')
CONFIG_FILE_PATH = os.environ.get('XINPU_CONFIG', 'config.json')
DATABASE_PATH = os.environ.get('XINPU_DB', 'cache.db')
IS_DRILL = os.environ.get('XINPU_DRILL')

class Application(object):
    def __init__(self, name='default'):
        self.name = name
        logging.info('[%s] starting up', self.name)

        # Set up database
        db.init(DATABASE_PATH)

        # Load configuration
        with open(CONFIG_FILE_PATH, 'r') as f:
            self.config = Config(**(json.load(f)))

        # Initialize shared services
        self.plurk = PlurkAPI.fromfile(API_KEY_PATH)
        self.is_drill = bool(IS_DRILL)

    def __del__(self):
        logging.info('[%s] shutting down', self.name)
