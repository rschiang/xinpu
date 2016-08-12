from datetime import datetime
from dateutil.tz import tzlocal
import dateutil.parser

def local_now():
    return datetime.now(tzlocal())

def parse_date(text):
    date = dateutil.parser.parse(text)
    if date.tzinfo:
        date = date.astimezone(tzlocal())
    return date
