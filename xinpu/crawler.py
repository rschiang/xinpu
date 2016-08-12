from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
from .plurkify import PlurkifyHTMLParser
from . import utils
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
            now = utils.local_now()

            # Iterate through feeds
            for feed in self.app.config.feeds:
                if feed.needs_update():
                    logging.info('Updating feed %s', feed.name)
                    new_entries = self.fetch_feed(feed)
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

        # Filter out new items
        entries = []
        for entry in news.entries:
            # See if the entry was processed before
            published = utils.parse_date(entry.published)
            if published > self.app.config.last_updated:
                item = self.parse_entry(feed, entry)
                item['date'] = published
                entries.append(item)
                logging.debug('Title %s', item['title'])

        return entries

    def parse_entry(self, feed, entry):
        # Read configutations
        extract_options = feed.options.get('extract', [])

        # Setup default values
        summary = entry.description
        item = {
            'site': feed.name,
            'title': entry.title,
            'url': entry.link,
            'image': '',
        }

        # Extract contents from site
        if 'follow' in feed.options or extract_options:
            request = urlopen(entry.link)

            # Replace proxied feed url with real ones
            item['url'] = urlparse(request.geturl()).geturl()  # Trim query strings

            if extract_options:
                soup = BeautifulSoup(request, 'html.parser')

                # Extract image from metadata if applicable
                if 'image' in extract_options:
                    image_tag = soup.find('meta', property='og:image')
                    if image_tag:
                        item['image'] = str(image_tag['content'])

                # Read description from metadata if applicable
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
