#!/usr/bin/env python
# coding=utf_8
import os
import time
import logging
from raven.contrib.tornado import SentryMixin
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from raven.contrib.tornado import AsyncSentryClient
import json
import subprocess

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='server.log',
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logging.getLogger('_mlogger').addHandler(console)
_mlogger = logging.getLogger('mylogger')
_mlogger.setLevel(logging.DEBUG)
_mlogger.debug("_mlogger start")

define("port", default=9003, help="run on the given port", type=int)
BASE_DIR = os.path.dirname(__file__)
print BASE_DIR
CONFIG_FILE = os.path.join(BASE_DIR, 'cfg.json')


def log_request_detail(func):
    def wrapper(handler, *args, **kwargs):
        debug_msg = "\n%s\nrequest url = %s \nrequest param = %s\n%s\n" \
                    % ('>' * 50,
                       handler.request.path,
                       handler.request.arguments,
                       "<" * 50)
        _mlogger.debug(debug_msg)
        print debug_msg
        return func(handler, *args, **kwargs)

    return wrapper


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

    def post(self, *args, **kwargs):
        self.write("ok")


def process_shell(cmd):
    """
    调用脚本的通用方法
    :param cmd:
    :param callback:
    :return:
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable="/bin/bash")
    returncode = None
    while returncode == None:
        returncode = p.poll()

    return returncode, p.stdout.read()

class HookHandler(SentryMixin, tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.write("ok")

    def post(self, *args, **kwargs):
        print 'request body==>', self.request.body
        data = json.loads(self.request.body)
        print data
        repository = data.get('repository', None)
        if repository:
            name = repository['name']
            cfg = json.loads(open(CONFIG_FILE, 'r').read())
            cmds = cfg[name]
            result = process_shell(cmds)
            response = result[1]
        else:
            response = data
        self.write(response)


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/githook/?", HookHandler),
    ])
    application.sentry_client = AsyncSentryClient(
        'https://5dda032172d341f6b678da68a567aaa3:0ac807330ce84bdb98e87faeb655187f@app.getsentry.com/62444'
    )
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
