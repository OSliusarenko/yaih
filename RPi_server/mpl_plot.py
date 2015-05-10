import tornado.ioloop
import tornado.web

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
from io import StringIO, BytesIO

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hello World!")

class ImgHandler(tornado.web.RequestHandler):
  def get(self, arg=1):

    arg=float(arg)
    xs = np.linspace(-10, 10, 1000)
    plt.plot(xs, np.sin(xs/arg), label='sin(x)')

    io = StringIO() #io = BytesIO()
    plt.savefig(io, format='svg') #plt.savefig(io, format='png')
    plt.close()
    self.set_header("Content-Type", "image/svg+xml")
    #self.set_header("Content-Type", "png")
    self.write(io.getvalue())

application = tornado.web.Application([
  (r"/", MainHandler),
  (r"/img", ImgHandler),
  (r"/img/(.*)", ImgHandler),
  ])

if __name__ == "__main__":
  application.listen(8080)
  tornado.ioloop.IOLoop.instance().start()
