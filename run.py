import tornado
from tornado import autoreload
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from app import app
from tornado.log import enable_pretty_logging
enable_pretty_logging()


app.debug = True
http_server = HTTPServer(WSGIContainer(app))
http_server.listen(1337)
ioloop = tornado.ioloop.IOLoop().instance()
autoreload.start(ioloop)
ioloop.start()

