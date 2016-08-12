from bs4 import BeautifulSoup
from datetime import datetime
from plurkify import PlurkifyHTMLParser
from urllib.request import urlopen
from urllib.parse import urlparse
import dateutil
import feedparser
import re
import threading

class FeedCrawler(threading.Thread):
    def __init__(self, app):
        super(FeedCrawler, self).__init__(name='crawler')
        self.app = app
        self.daemon = True

    def run(self):
        while self.app.running():
            plurkifier = PlurkifyHTMLParser()
            entries = []
            for feed in config.feeds:
                if not feed.needs_update():
                    continue

                # Fetch new feed
                news = feedparser.parse(feed.url)
                extract_options = feed.options.get('extract', [])

                # Filter out new items
                for entry in news.entries:
                    published = dateutil.parser.parse(entry.published)
                    if published <= feed.last_updated:
                        continue

                    item = {
                        'site': feed.name,
                        'title': entry.title,
                        'url': entry.link,
                        'date': published,
                    }

                    if 'description' not in extract_options:
                        summary = plurkifier.convert(entry.description)

                        # Pass through content filter if needed
                        if 'content_filter' in feed.options:
                            summary = re.sub(feed.options['content_filter'], '', summary)

                        item['summary'] = summary.strip()

                    # TODO: Extract contents from site
                    if 'follow' in feed.options or extract_options:
                        request = urlopen(entry.link)
                        link = urlparse(request.geturl()).geturl()  # Trim query strings

                        if extract_options:
                            soup = BeautifulSoup(request)

                    entries.append(item)

            # After aggregating all feeds, sort them before post
            entries = sorted(entries, key=lambda i: i['date'])
            for item in entries:
                self.app.post_item(item)
