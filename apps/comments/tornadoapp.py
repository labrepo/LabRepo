import datetime
import json
import time
import urllib

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


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.write('Hello. :)')


class MessagesHandler(tornado.websocket.WebSocketHandler):

    def my_handler(self, message):
        if message.kind == 'message':
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
        # self.client.listen(self.on_message)

    def open(self, channel):
        self.channel = channel
        self.listen()
        # session_key = self.get_cookie(settings.SESSION_COOKIE_NAME)
        # session = session_engine.SessionStore(session_key)
        # try:
        #     self.user_id = session["_auth_user_id"]
        #     self.sender_name = User.objects.get(id=self.user_id).username
        # except (KeyError, User.DoesNotExist):
        #     self.close()
        #     return
        # if not Thread.objects.filter(
        #     id=thread_id,
        #     participants__id=self.user_id
        # ).exists():
        #     self.close()
        #     return


    def handle_request(self, response):
        pass

    def on_message(self, message):
        print(message)
        # if not message:
        #     return
        # if len(message) > 10000:
        #     return
        # c.publish(self.channel, json.dumps({
        #     "timestamp": int(time.time()),
        #     "sender": self.sender_name,
        #     "text": message,
        # }))
        # http_client = tornado.httpclient.AsyncHTTPClient()
        # request = tornado.httpclient.HTTPRequest(
        #     "".join([
        #                 settings.SEND_MESSAGE_API_URL,
        #                 "/",
        #                 self.thread_id,
        #                 "/"
        #             ]),
        #     method="POST",
        #     body=urllib.urlencode({
        #         "message": message.encode("utf-8"),
        #         "api_key": settings.API_KEY,
        #         "sender_id": self.user_id,
        #     })
        # )
        # http_client.fetch(request, self.handle_request)
        self.write_message(str('123'))


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
