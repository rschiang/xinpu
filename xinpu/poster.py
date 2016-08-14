import logging
import threading
from plurk_oauth import PlurkAPI
from queue import Queue

class ContentPoster(threading.Thread):
    def __init__(self, app):
        super(ContentPoster, self).__init__(name='poster')
        self.app = app
        self.daemon = True
        self.queue = Queue()
        self.cache = {}
        self.plurk = PlurkAPI.fromfile('plurk.json')

    def run(self):
        while self.app.running():
            if self.queue.empty():
                continue

            item = self.queue.get()
            if item['url'] in self.cache:
                logging.warn('Duplicated entry %s (%s)', item['title'], item['site'])
                logging.info('Cached date: %s, entry date: %s',
                             item['date'].isoformat(' '), self.cache[item['url']].isoformat(' '))
            else:
                self.append_to_cache(item['url'], item['date'])

            content = self.app.config.format.format(**item).strip()
            result = self.plurk.callAPI('/APP/Timeline/plurkAdd', {
                'qualifier': ':',
                'content': content,
                'lang': item.get('lang', self.app.config.lang),
            })

            if not result:
                logging.warn('Failed to post content %s (%s)', item['title'], item['site'])
                logging.debug(self.plurk.error())

    def append_to_cache(self, url, date):
        if len(self.cache > 200):
            oldest = min(self.cache.keys(), key=lambda i: self.cache[i])
            del self.cache[oldest]
        self.cache[url] = date
