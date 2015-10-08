import threading

class ContentPoster(threading.Thread):
    def __init__(self, app):
        super(ContentPoster, self).__init__(name='poster')
        self.app = app
        self.daemon = True
        self.queue = Queue()

    def run(self):
        while self.app.running():
            if self.queue.empty():
                continue

            item = self.queue.get()
            # Post item
