import threading
from plurk_oauth import PlurkAPI

class ContentPoster(threading.Thread):
    def __init__(self, app):
        super(ContentPoster, self).__init__(name='poster')
        self.app = app
        self.daemon = True
        self.queue = Queue()
        self.api = PlurkAPI.fromfile('plurk.json')

    def run(self):
        while self.app.running():
            if self.queue.empty():
                continue

            item = self.queue.get()
            content = self.app.config.format.format(**item).strip()

            result = plurk.callAPI('/APP/Timeline/plurkAdd', {
                'qualifier': ':',
                'content': content,
                'lang': item.get('lang', self.app.config.lang),
            })
