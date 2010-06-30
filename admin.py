import logging

# App Engine imports
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template

import urllib
import json
import os
import sys

app_id = 'bugtracky'

class Admin:
  """Initializes the list of gifts in the datastore."""

  def get(self):
    self.response.out.write('yes!')

class Item(db.Model):
    project_id = db.StringProperty()
    status_config = db.StringProperty()
    assignee_config = db.StringProperty()
    type_config = db.StringProperty()
    priority_config = db.StringProperty()
    updated_by = db.StringProperty()

class AdminServer(webapp.RequestHandler):
  """Handles requests to /admin URLs and delegates to the Admin class."""
  def _handleRequest(self):
    user = users.get_current_user()
    if user:
      if users.is_current_user_admin():
        email = user.email();
        dictionary = {}
        dictionary['greetings'] = ("Welcome, %s! (<a href=\"%s\">Sign out</a>)" %
                    (user.nickname(), users.create_logout_url("/controlpanel")))
        self.RenderTemplate('templates/admin.html', dictionary)
      else:
        self.response.out.write('Permission denied.')
    else:
      greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/controlpanel"))
    #self.response.out.write(json.write({'error': '0'}))

  def RenderTemplate(self, filename, dictionary):
    """Render the given template definition file with the given dictionary.

    Args:
      filename: The filename of the template to expand.
      dict: The dictionary that contains the values to populate in the template.
    """
    path = os.path.join(os.path.dirname(__file__), filename)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(path, dictionary))

  def FetchSettings(self):
    logging.error('start fetch settings')
    item = {}
    try:
      query = 'Select * from Item WHERE project_id=\'bugtracky\''
      items = db.GqlQuery(query)
      for row in items:
        item = {
          'id': row.project_id,
          'statusConfig': row.status_config,
          'assigneeConfig': row.assignee_config,
          'typeConfig': row.type_config,
          'priorityConfig': row.priority_config,
          'updatedBy': row.updated_by
        }
    except:
      item = {'error': '1'}
    logging.error(item)
    return item

  def GetConfig(self):
    item = self.FetchSettings()
    self.response.out.write(json.write(item))

  def SaveConfig(self, params):
    user = users.get_current_user()
    if user:
      user = user.nickname()
    id = params['id']
    if id == app_id:
      new_item = True
      results = Item.gql("WHERE project_id = :1", app_id)
      for row in results:
        new_item = False
        item = row
      if new_item:
        item = Item()
      item.project_id = id
      item.status_config = params['statusConfig']
      item.assignee_config = params['assigneeConfig']
      item.type_config = params['typeConfig']
      item.priority_config = params['priorityConfig']
      item.updated_by = user
      item.put()
      self.response.out.write(json.write({'error': '0'}))
    else:
      self.response.out.write(json.write({'error': '1'}))

  def get(self):
    """Ensure that the user is an admin, then invoke appropriate action."""
    if self.request.path.startswith('/controlpanel'):
      self._handleRequest()
    elif self.request.path.startswith('/debug_settings'):
      self.GetConfig()

  def post(self):
    if self.request.path.startswith('/controlpanel'):
      self.DoAction()
    elif self.request.path.startswith('/retrievesettings'):
      self.GetConfig()

  def DoAction(self):
    post_data = self.request.POST
    for config in post_data:
      post_data = config
    post_data = json.read(post_data.encode('utf8'))
    method = post_data['method']
    params = post_data['params']
    if method == 'GET_CONFIG_PARAM':
      self.GetConfig()
    elif method == 'SAVE_CONFIG_PARAM':
      self.SaveConfig(params)
