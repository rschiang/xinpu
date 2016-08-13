from bs4 import BeautifulSoup
from datetime import timedelta
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

                    # Marked the completion of this interval
                    feed.last_checked = now
                    if new_entries:
                        entries += new_entries  # Some feeds does not immediately reflect
                        feed.last_updated = now # new articles, update time lazily
                    elif (now - feed.last_updated).total_seconds() > self.app.config.backtrack:
                        # Push last_updated forward as entries before this time should be ignored
                        feed.last_updated = now - timedelta(seconds=self.app.config.backtrack)
                    else: continue

                    # Update last_updated
                    self.app.save_last_update()

            # After aggregating all feeds, sort them before post
            entries = sorted(entries, key=lambda i: i['date'])
            for item in entries:
                self.app.post_item(item)


    def fetch_feed(self, feed):
        # Fetch feed
        news = feedparser.parse(feed.url)

        # Filter out new items
        entries = []
        for entry in news.entries:
            # See if the entry was processed before
            published = utils.parse_date(entry.published)
            if published > feed.last_updated:
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
        title = self.truncate_text(entry.title, 40)
        summary = entry.description
        item = {
            'site': feed.name,
            'title': title,
            'url': entry.link,
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
            return text[:length-1] + '…'
        return text

    def extract_image(self, feed, soup):
        url = None

        if 'image_selector' in feed.options:
            tag = soup.select_one(feed.options['image_selector'])
            if tag: url = str(tag['src'])

        if not url:
            tag = soup.find('meta', property='og:image')
            if tag: url = str(tag['content'])
            else: return

        if 'image_exclude' in feed.options:
            if url in feed.options['image_exclude']: return

        return url

    def extract_summary(self, feed, soup):
        tag = soup.find('meta', property='og:description') or soup.find('meta', name='description')
        if tag:
            return str(tag['content'])
