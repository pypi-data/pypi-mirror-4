from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, RequestHandler, Application
from raspberry_jam import app

class MainHandler(RequestHandler):
        def get(self):
                self.write('Tornado ftw')

tr = WSGIContainer(app)

application = Application([
        (r'/tornado', MainHandler),
        (r'.*', FallbackHandler, dict(fallback=tr)),
])

if __name__ == '__main__':
        application.listen(8000)
        IOLoop.instance().start()
