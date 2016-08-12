from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlparse
from .plurkify import PlurkifyHTMLParser
import dateutil
import feedparser
import logging
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
            now = datetime.now()

            # Iterate through feeds
            for feed in self.app.config.feeds:
                if feed.needs_update():
                    logging.info('Updating feed {}', feed.name)
                    new_entries = fetch_feed(feed)
                    entries += new_entries

            # After aggregating all feeds, sort them before post
            entries = sorted(entries, key=lambda i: i['date'])
            for item in entries:
                self.app.post_item(item)

            # Update last_updated
            self.app.set_last_update(now)

    def fetch_feed(self, feed):
        # Fetch feed
        news = feedparser.parse(feed.url)
        extract_options = feed.options.get('extract', [])

        # Filter out new items
        entries = []
        for entry in news.entries:
            # See if the entry was processed before
            published = dateutil.parser.parse(entry.published)
            if published > feed.last_updated:
                item = self.parse_entry(feed, entry)
                item['date'] = published
                entries.append(item)

        return entries

    def parse_entry(self, feed, entry):
        item = {
            'site': feed.name,
            'title': entry.title,
            'url': entry.link,
            'image': '',
        }

        # Extract default values
        summary = entry.description

        # Extract contents from site
        if 'follow' in feed.options or extract_options:
            request = urlopen(entry.link)

            # Replace proxied feed url with real ones
            item['url'] = urlparse(request.geturl()).geturl()  # Trim query strings

            if extract_options:
                soup = BeautifulSoup(request)

                if 'image' in extract_options:
                    image_tag = soup.find('meta', property='og:image')
                    if image_tag:
                        item['image'] = str(image_tag['content'])

                if 'description' in extract_options:
                    summary_tag = soup.find('meta', property='og:description') or soup.find('meta', name='description')
                    if summary_tag:
                        summary = str(summary_tag['content'])

        # Postprocessing summary
        summary = self.plurkifier.convert(summary)

        # Pass through content filter if needed
        if 'content_filter' in feed.options:
            summary = re.sub(feed.options['content_filter'], '', summary)

        item['summary'] = summary.strip()

        return item
