#!/usr/bin/python2.5
#
# Copyright 2010 Google Inc. All Rights Reserved.
"""To check whether set of robot is done correctly."""


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from admin import AdminServer

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('Some thing happened..')


class VerifyHandler(webapp.RequestHandler):

  def get(self):
    st = self.request.get('st', '')
    if st == '8636' :
      self.response.out.write('KEY')
    else:
      self.response.out.write('Invalid key')

def main():
  application = webapp.WSGIApplication([(r'/_wave/verify_token.*', VerifyHandler),
                                        (r'/controlpanel', AdminServer),
                                        (r'/retrievesettings', AdminServer),
                                        (r'/.*', MainHandler)],
                                        debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
