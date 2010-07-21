import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

import common

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('Welcome to Issue Tracky!')

class XmlHandler(webapp.RequestHandler):

  def RenderTemplate(self, filename, dictionary={}):
    dictionary['server'] = common.GetServer()
    path = os.path.join(os.path.dirname(__file__), 'templates/' + filename)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(path, dictionary))

class GadgetHandler(XmlHandler):
  def get(self):
    self.RenderTemplate('gadget.xml')

class InstallerHandler(XmlHandler):
  def get(self):
    dictionary = {}
    dictionary['icon_url'] = common.GetIconUrl()
    dictionary['avatar_url'] = common.GetAvatarUrl()
    dictionary['robot_address'] = common.GetRobotAddress()
    dictionary['robot_key'] = common.ROBOT_KEY
    self.RenderTemplate('installer.xml', dictionary)

def main():
  application = webapp.WSGIApplication([(r'/installer.xml', InstallerHandler),
                                        (r'/gadget.xml', GadgetHandler),
                                        (r'/.*', MainHandler)],
                                        debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
