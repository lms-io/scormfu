from bottle import route, run, response
from time import sleep
import redis, configparser, thread, requests, sys, bottle

from src import api 
class EnableCors(object):
  name = 'enable_cors'
  api = 2

  def apply(self, fn, context):
    def _enable_cors(*args, **kwargs):
      # set CORS headers
      response.headers['Access-Control-Allow-Origin'] = '*'
      response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
      response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

      if bottle.request.method != 'OPTIONS':
        # actual request; reply with the actual response
        return fn(*args, **kwargs)

    return _enable_cors


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
app = bottle.app()
app.install(EnableCors())
run(app=StripPathMiddleware(app),host=bhost, port=bport, debug=bdebug, server='cherrypy')
