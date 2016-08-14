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
        self.plurk = PlurkAPI.fromfile('plurk.json')
        self.cache = []
        try:
            with open('cache.txt', 'r') as f:
                self.cache = [line.strip() for line in f]
        except FileNotFoundError:
            logging.warning('No cache file present')

    def run(self):
        while self.app.running():
            if self.queue.empty():
                continue

            item = self.queue.get()
            url = item['url'].strip()
            if url in self.cache:
                logging.warn('Duplicated entry %s (%s)', item['title'], item['site'])
                continue

            content = self.app.config.format.format(**item).strip()
            result = self.plurk.callAPI('/APP/Timeline/plurkAdd', {
                'qualifier': ':',
                'content': content,
                'lang': item.get('lang', self.app.config.lang),
            })

            if not result:
                logging.warn('Failed to post content %s (%s)', item['title'], item['site'])
                logging.debug(self.plurk.error())
            else:
                self.cache.append(url)
                try:
                    with open('cache.txt', 'a') as f:
                        f.write(url + '\n')
                except:
                    logging.exception('Error while writing cache %s', url)
