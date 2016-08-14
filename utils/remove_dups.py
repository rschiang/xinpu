#!/usr/bin/env python
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from dateutil.tz import tzutc, tzlocal
from plurk_oauth import PlurkAPI

class Plurk(object):
    def __init__(self, plurk_id, posted, content_raw, **kwargs):
        self.plurk_id = plurk_id
        self.posted = parse_date(posted)
        self.content_raw = content_raw
    def __hash__(self):
        return self.plurk_id

plurk = PlurkAPI.fromfile('plurk.json')
start = datetime.now(tzlocal())
end = start - timedelta(hours=24)

plurks = []
while start > end:
    print('Fetching', start)
    resp = plurk.callAPI('/APP/Timeline/getPlurks', {
        'filter': 'my',
        'limit': 30,
        'offset': start.astimezone(tzutc()).isoformat() })
    plurks.extend(Plurk(**p) for p in resp['plurks'])
    start = min(plurks, key=lambda x: x.posted).posted

titles = set()
unique_plurks = sorted(set(plurks), key=lambda x: x.posted)
print('Unique plurks', len(unique_plurks))

for p in unique_plurks:
    title = p.content_raw[:p.content_raw.find('\n')].strip()
    if title in titles:
        print('Removing duplicate title', title)
        print(plurk.callAPI('/APP/Timeline/plurkDelete', {'plurk_id': p.plurk_id }))
    else:
        titles.add(title)

print('Unique titles', len(titles))
