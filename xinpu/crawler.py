from bs4 import BeautifulSoup
from datetime import timedelta
from urllib.request import urlopen
from .app import Application
from .models import Item
from .plurkify import PlurkifyHTMLParser
from . import utils
import feedparser
import logging
import re

class FeedCrawler(Application):
    def __init__(self):
        super().__init__('crawler')
        self.plurkifier = PlurkifyHTMLParser()

    def run(self):
        now = utils.local_now()

        # Iterate through feeds
        for feed in self.config.feeds:
            if not feed.needs_update():
                continue

            logging.info('[crawler] updating feed %s', feed.name)

            try:
                new_items = self.fetch_feed(feed)
            except:
                logging.exception('cannot connect to feed')
                continue

            # Marked the completion of this interval
            feed.last_checked = now
            if new_items:
                # Save them into queue
                Item.insert_many(new_items).execute()
                # Some feeds does not immediately reflect new articles, update time lazily
                feed.last_updated = now
            else:
                # Check if feed has stagnated over backtrack window
                if (now - feed.last_updated).total_seconds() > self.config.backtrack:
                    # Push last_updated forward as entries before this time should be ignored
                    feed.last_updated = now - timedelta(seconds=self.config.backtrack)

    def fetch_feed(self, feed):
        # Fetch feed
        news = feedparser.parse(feed.url)
        items = []

        # Filter out new items
        for entry in news.entries:
            # See if the entry was processed before
            published = utils.parse_date(entry.published)
            if published > feed.last_updated:
                # Check if URL existed before
                if Item.select().where(Item.url == entry.link.strip()).exists():
                    logging.warn('[crawler] duplicate entry %s', entry.link)
                    continue

                # Parse and extract its content
                item = self.parse_entry(feed, entry)
                item['date'] = published

                # Add to queue
                logging.debug('[crawler] title %s', item['title'])
                items.append(item)

        return items

    def parse_entry(self, feed, entry):
        # Read feed configuration
        follow_link = (feed.options.get('link') == 'follow')
        extract_options = feed.options.get('extract', [])

        # Setup default values
        title = self.truncate_text(entry.title, 40)
        summary = entry.description
        item = {
            'site': feed.name,
            'title': title,
            'url': entry.link.strip(),
            'image': '',
            }

        # Extract contents from site
        if follow_link or extract_options:
            try:
                request = urlopen(entry.link)
            except:
                logging.exception('Cannot connect to %s', entry.link)
            else:
                # Replace proxied feed url with real ones
                if follow_link:
                    url, _, qs = request.geturl().partition('?')
                    item['url'] = url

                if extract_options:
                    soup = BeautifulSoup(request, 'html.parser')

                    # Extract image from metadata if applicable
                    if 'image' in extract_options:
                        item['image'] = self.extract_image(feed, soup) or ''

                    # Read description from metadata if applicable
                    if 'description' in extract_options:
                        summary = self.extract_summary(feed, soup) or summary

        # Postprocessing summary
        self.plurkifier.feed(summary)
        self.plurkifier.close()
        summary = self.plurkifier.getvalue()
        self.plurkifier.reset()

        # Pass through content filter if needed
        if 'content_filter' in feed.options:
            summary = re.sub(feed.options['content_filter'], '', summary).strip()

        # Truncate string if needed
        item['summary'] = self.truncate_text(summary, 100)
        return item

    def truncate_text(self, text, length):
        if len(text) > length:
            return text[:length - 1] + '…'
        return text

    def extract_image(self, feed, soup):
        url = None

        if 'image_selector' in feed.options:
            tag = soup.select_one(feed.options['image_selector'])
            if tag:
                url = str(tag['src'])

        if not url:
            tag = soup.find('meta', property='og:image')
            if tag:
                url = str(tag['content'])
            else:
                return

        if 'image_exclude' in feed.options:
            if url in feed.options['image_exclude']:
                return

        return url

    def extract_summary(self, feed, soup):
        tag = soup.find('meta', property='og:description') or soup.find('meta', attrs={'name': 'description'})
        if tag:
            return str(tag['content'])
