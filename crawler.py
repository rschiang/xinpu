from datetime import datetime
from plurkify import plurkify_text
import dateutil
import threading
import feedparser

class FeedCrawler(threading.Thread):
    def __init__(self, app):
        super(FeedCrawler, self).__init__(name='crawler')
        self.app = app
        self.daemon = True

    def run(self):
        while self.app.running():
            entries = []
            for feed in config.feeds:
                if not feed.needs_update():
                    continue

                # Fetch new feed
                news = feedparser.parse(feed.url)

                # Filter out new items
                for entry in news.entries:
                    published = dateutil.parser.parse(entry.published)
                    if published <= feed.last_updated:
                        continue

                    item = {
                        'site': feed.name,
                        'title': entry.title,
                        'url': entry.link,
                        'summary': plurkify_text(entry.description),
                        'date': published,
                    }

                    # TODO: Extract contents from site
                    entries.append(item)

            # After aggregating all feeds, sort them before post
            entries = sorted(entries, key=lambda i: i['date'])
            for item in entries:
                self.app.post_item(item)
