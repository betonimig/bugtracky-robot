import os

ROBOT_KEY = 'robot.issuetracker.request'
BUG_KEY = 'robot.issuetracker.id'
PREVIEW_RPC_BASE = 'http://gmodules.com/api/rpc'

def GetIconUrl():
  return '%s/img/icon.png' % GetServer()

def GetAvatarUrl():
  return '%s/img/avatar.png' % GetServer()

def GetGadgetUrl():
  return '%s/gadget.xml' % GetServer()

def GetInstallerUrl(id):
  return '%s/installer.xml' % (GetServer(), id)

def GetServer():
  server = os.environ['SERVER_NAME']
  port = os.environ['SERVER_PORT']

  if port and port != '80':
    return 'http://%s:%s' % (server, port)
  else:
    return 'http://%s' % (server)

def GetRobotAddress():
  server = os.environ['SERVER_NAME']
  app_id = server.split('.')[0]
  return '%s@appspot.com' % app_id

def GetRPCBase(domain):
  if domain == 'wavesandbox.com':
    return 'http://www-opensocial-sandbox.googleusercontent.com/api/rpc'
  else:
    return 'http://www-opensocial.googleusercontent.com/api/rpc'
