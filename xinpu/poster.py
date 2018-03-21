import logging
from .app import Application
from .models import Item

class ContentPoster(Application):
    def __init__(self):
        super().__init__(name='poster')

    def run(self):
        item = Item.select().where(Item.posted == False).order_by(Item.date).first()    # noqa: E712
        if not item:
            # There's nothing we could post now
            return

        content = self.config.format.format(**item).strip()
        if not self.drill:
            result = self.plurk.callAPI('/APP/Timeline/plurkAdd', {
                'qualifier': ':',
                'content': content,
                'lang': self.config.lang,
                })
        else:
            logging.debug('[poster] post %s', content)
            result = True

        if not result:
            logging.warn('[poster] failed to post content <%s> %s', item.site, item.title)
            logging.debug(self.plurk.error())
            return

        item.posted = True
        item.save()
