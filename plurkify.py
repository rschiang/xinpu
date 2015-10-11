import bleach
import re

ALLOWED_TAGS = (
    'a', 'b', 'br', 'code', 'del', 'em', 'i', 'img', 'p', 's', 'strike', 'strong', 'u',
)

ALLOWED_ATTRIBUTES = {
    'a': ('href',),
    'img': ('src', 'alt'),
}

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

def plurkify_text(text):
    raw_text = bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    raw_text = linkify(raw_text)
    raw_text = linkify_image(raw_text)
    raw_text = reformat(raw_text)
    return html.unescape(raw_text)
