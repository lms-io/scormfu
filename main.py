from bottle import route, run
from time import sleep
import redis, configparser, thread, requests, sys, bottle

from src import api 


class StripPathMiddleware(object):
  def __init__(self, app):
    self.app = app
  def __call__(self, e, h):
    e['PATH_INFO'] = e['PATH_INFO'].rstrip('/')
    return self.app(e,h)

config = configparser.ConfigParser()
config.read('config.ini')
bhost = config.get('bottle','host')
bport = config.getint('bottle','port')
bdebug = config.getboolean('bottle','debug')
run(app=StripPathMiddleware(bottle.app()),host=bhost, port=bport, debug=bdebug)
