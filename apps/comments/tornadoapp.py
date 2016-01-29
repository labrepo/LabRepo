import redis
import tornadoredis

import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.httpclient
import tornado.gen
import tornado.httpserver

from django.conf import settings
from django.utils.importlib import import_module

session_engine = import_module(settings.SESSION_ENGINE)

r = redis.StrictRedis(host='localhost', port=6379, db=3)
p = r.pubsub()
c = tornadoredis.Client()
c.connect()


class MessagesHandler(tornado.websocket.WebSocketHandler):

    def my_handler(self, message):
        if message.kind == 'message':
            if settings.DEBUG:
                print(message.body)
            try:
                self.write_message(str(message.body))
            except TypeError:
                pass

        if message.kind == 'disconnect':
            # Do not try to reconnect, just send a message back
            # to the client and close the client connection
            self.write_message('The connection terminated')
            self.close()

    def __init__(self, *args, **kwargs):
        super(MessagesHandler, self).__init__(*args, **kwargs)

    @tornado.gen.engine
    def listen(self):
        self.client = tornadoredis.Client()
        self.client.connect()
        yield tornado.gen.Task(self.client.subscribe, self.channel)
        self.client.listen(self.my_handler)

    def open(self, channel):
        self.channel = channel
        self.listen()

    def handle_request(self, response):
        pass

    def on_message(self, message):
        pass

    def show_new_message(self, result):
        self.write_message(str(result.body))

    def on_close(self):
        if self.client.subscribed:
            self.client.unsubscribe(self.channel)
            self.client.disconnect()

    def check_origin(self, origin):
        return True


application = tornado.web.Application([
    (r"/", MessagesHandler),
    (r'/chat/(?P<channel>\d+)/', MessagesHandler),
])
