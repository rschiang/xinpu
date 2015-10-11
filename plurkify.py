import bleach
import html
import re

ALLOWED_TAGS = (
    'a', 'b', 'br', 'code', 'del', 'em', 'i', 'img', 'p', 's', 'strike', 'strong', 'u',
)

ALLOWED_ATTRIBUTES = {
    'a': ['href'],
    'img': ['src', 'alt'],
}

SCRIPTINATOR = re.compile(r'\<script[^\>]*\>.*?\</script\>', re.IGNORECASE | re.DOTALL)

WHITESPACEINATOR = re.compile(r'\s{2,}')

LINKIFIER = re.compile(r'\<a href=[\'"]?(?P<url>[^\'"\>]+)[\'"]?\>(?P<title>[^\>]+?)\</a\>', re.IGNORECASE)

IMAGE_LINKIFIER = re.compile(r'\<img(\s*src=[\'"]?(?P<url>[^\'"\>]+)[\'"]?\s*|\s*alt=[\'"]?(?P<title>[^\'"\>]+)[\'"]?\s*)*/?\>', re.IGNORECASE)

TAG_GRINDER = re.compile(r'\<(?P<tag>[^\>]+?)\>')

FORMATTERS = {
    '**': ('b', 'strong'),
    '*': ('i', 'em'),
    '--': ('del', 's', 'strike'),
    '`': ('code',),
    '__': ('u',),
    '\n': ('br', 'p'),
}

def remove_scripts(text):
    return SCRIPTINATOR.sub('', text)

def remove_spaces(text):
    def formatter(match):
        return '\n' if '\n' in match.group(0) else ' '
    return WHITESPACEINATOR.sub(formatter, text)

def linkify(text):
    return LINKIFIER.sub(r'\g<url> (\g<title>)', text)

def linkify_image(text):
    return IMAGE_LINKIFIER.sub(r'\g<url> (\g<title>)', text)

def reformat(text):
    def formatter(match):
        tag = match.group('tag').lower().strip('/ ')
        for char, tags in FORMATTERS.items():
            if tag in tags:
                return char
        return ''
    return TAG_GRINDER.sub(formatter, text).strip()

def clean_tags(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

def plurkify_text(text):
    for process in (remove_scripts, clean_tags, linkify, linkify_image, reformat, html.unescape, remove_spaces):
        text = process(text)
    return text
