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
        self.plurkifier = PlurkifyHTMLParser()

    def run(self):
        while self.app.running():
            entries = []
            for feed in config.feeds:
                if feed.needs_update():
                    new_entries = fetch_feed(feed)
                    entries += new_entries

            # After aggregating all feeds, sort them before post
            entries = sorted(entries, key=lambda i: i['date'])
            for item in entries:
                self.app.post_item(item)

    def fetch_feed(self, feed):
        # Fetch feed
        news = feedparser.parse(feed.url)
        extract_options = feed.options.get('extract', [])

        # Filter out new items
        entries = []
        for entry in news.entries:
            item = self.parse_entry(feed, entry)
            if item:
                entries.append(item)

        return entries

    def parse_entry(self, feed, entry):
        # Skip the entry if already updated
        published = dateutil.parser.parse(entry.published)
        if published <= feed.last_updated:
            return None

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
