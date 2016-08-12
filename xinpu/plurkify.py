from html.parser import HTMLParser
from io import StringIO
import re

WHITESPACEINATOR = re.compile(r'\s{2,}')

FORMATTERS = {
    'b': '**',
    'code': '`',
    'del': '--',
    'em': '*',
    'i': '*',
    'p': '\n',
    's': '--',
    'strike': '--',
    'strong': '**',
    'u': '__',
}

class PlurkifyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.buffer = StringIO()
        self.current_url = None
        self.sub_buffer = StringIO()

    # Public functions
    @staticmethod
    def convert(text):
        parser = PlurkifyHTMLParser()
        parser.feed(text)
        parser.close()
        return parser.getvalue()

    def close(self):
        super().close()
        # Close all remaining tags
        while self.stack:
            top = self.stack.pop()
            self.close_tag(tag)

    def reset(self):
        super().reset()
        self.buffer.close()
        self.buffer = StringIO()

    def getvalue(self):
        value = self.buffer.getvalue()
        return PlurkifyHTMLParser.remove_spaces(value).strip()

    # Internal functions

    def handle_starttag(self, tag, attrs):
        # Skip line breaks
        if tag == 'br':
            self.write_buffer('\n')
            return

        # Push current tag to stack
        self.stack.append(tag)

        # Append formatter prefix
        if tag in FORMATTERS:
            self.write_buffer(FORMATTERS[tag])
        elif tag == 'a':
            attributes = dict(attrs)
            self.current_url = attributes.get('href')

    def handle_data(self, data):
        if not self.is_in_raw_tag():
            self.write_buffer(data)

    def handle_endtag(self, tag):
        # Close tag if tag is not in stack
        if tag not in self.stack:
            self.close_tag(tag)
            return

        # Properly close tag if misplaced
        while self.stack:
            # Close the current tag on stack
            top = self.stack.pop()
            self.close_tag(top)

            # All remaining tags popped
            if top == tag:
                break

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.write_buffer('\n')
        elif tag == 'img':
            attributes = dict(attrs)
            url = attributes.get('src', '').strip()
            title = attributes.get('alt', '').strip()

            # Note that we write to buffer directly
            # since it's impossible to place image inside hyperlink on Plurk
            if url:
                self.buffer.write(url)
            if title:
                self.buffer.write(' ({})'.format(title))

    # Utilities function

    def is_in_raw_tag(self):
        return 'script' in self.stack or 'style' in self.stack

    def write_buffer(self, text):
        if 'a' in self.stack:
            self.sub_buffer.write(text)
        else:
            self.buffer.write(text)

    def is_valid_url(self, url):
        for prefix in ('#', 'javascript'):
            if url.startswith(prefix):
                return False
        return True

    def close_tag(self, tag):
        # Append formatter postfix
        if tag in FORMATTERS:
            self.buffer.write(FORMATTERS[tag])
        elif tag == 'a':
            url = self.current_url
            title = self.sub_buffer.getvalue().strip()

            if url and self.is_valid_url(url):
                if title:
                    self.buffer.write('{} ({})'.format(url, title))
                else:
                    self.buffer.write(url)  # URL only
            else:
                self.buffer.write(title)   # Plain text

            # Reset sub-buffer
            self.current_url = None
            self.sub_buffer.close()
            self.sub_buffer = StringIO()

    @staticmethod
    def remove_spaces(text):
        def formatter(match):
            return '\n' if '\n' in match.group(0) else ' '
        return WHITESPACEINATOR.sub(formatter, text)
