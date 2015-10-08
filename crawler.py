import threading

class FeedCrawler(threading.Thread):
    def __init__(self, app):
        super(FeedCrawler, self).__init__(name='crawler')
        self.app = app
        self.daemon = True

    def run(self):
        while self.app.running():
            for feed in config.feeds:
                if not feed.needs_update():
                    continue
                # Fetch new feed
