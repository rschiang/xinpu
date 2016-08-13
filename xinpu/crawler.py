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
                    feed.last_updated = now

            # After aggregating all feeds, sort them before post
            entries = sorted(entries, key=lambda i: i['date'])
            for item in entries:
                self.app.post_item(item)

            # Update last_updated
            self.app.config.last_updated = now
            self.app.save_last_update()

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
        follow_link = (feed.options.get('link') == 'follow')
        extract_options = feed.options.get('extract', [])

        # Setup default values
        title = entry.title
        summary = entry.description
        item = {
            'site': feed.name,
            'url': entry.link,
            'image': '',
        }

        # Extract contents from site
        if follow_link or extract_options:
            request = urlopen(entry.link)

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
        if len(title) > 40:
            title = title[:40].strip() + '…'
        if len(summary) > 100:
            summary = summary[:100].strip() + '…'
        item['summary'] = summary

        return item

    def extract_image(self, feed, soup):
        tag = soup.find('meta', property='og:image')
        if not tag: return

        url = str(tag['content'])
        if 'exclude_images' in feed.options:
            if url in feed.options['exclude_images']: return

        return url

    def extract_summary(self, feed, soup):
        tag = soup.find('meta', property='og:description') or soup.find('meta', name='description')
        if tag:
            return str(tag['content'])
