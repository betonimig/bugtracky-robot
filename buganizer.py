#!/usr/bin/python2.5
#
# Copyright 2010 Google Inc. All Rights Reserved.
"""Robot that creates a wave for an issue."""

import time
import logging

from waveapi import appengine_robot_runner
from waveapi import element
from waveapi import events
from waveapi import robot

from google.appengine.ext import db
from admin import AdminServer

CONSUMER_KEY = 'CONSUMER_KEY'
CONSUMER_SECRET = 'CONSUMER_SECRET'
ROBOT_KEY = 'robot.bugtracky.request'
ROBOT_ID = u'bugtracky@appspot.com'
BUG_KEY = 'robot.bugtracky.id'
SANDBOX_RPC_BASE = 'http://sandbox.gmodules.com/api/rpc'
PREVIEW_RPC_BASE = 'http://gmodules.com/api/rpc'
GADGET_URL = 'http://bugtracky.appspot.com/buganizer.xml'
ICON = 'http://bugtracky.appspot.com/icon.png'


def OnAnnotationChanged(event, wavelet):
  logging.error('OnAnnotationChanged')
  """Called when the annotation changes."""
  blip = event.blip
  todo = []

  for ann in blip.annotations:
    if ann.name == ROBOT_KEY:
      todo.append((ann.start, ann.end))

  query = 'Select * from Item WHERE project_id=\'bugtracky\''
  items = db.GqlQuery(query)
  status = ''
  assignee = ''
  type = ''
  priority = ''
  for row in items:
    status = str(row.status_config)
    assignee = str(row.assignee_config)
    type = str(row.type_config)
    priority = str(row.priority_config)

  msgtext = ''
  if assignee != '':
    assignee = event.modified_by
    msgtext = ' (Assigned: ' + event.modified_by
  else:
    assignee = '-1'
  if status != '':
    status = 'New'
    if msgtext == '':
      msgtext = ' ('
    else:
      msgtext = msgtext + ', '
    msgtext = msgtext + 'Status: ' + status + ') '
  else:
    status = '-1'
  if priority != '':
    priority = '2'
  else:
    priority = '-1'
  if type != '':
    type = 'bug'
  else:
    type = '-1'

  bug_robot.setup_oauth(CONSUMER_KEY,
                        CONSUMER_SECRET,
                        server_rpc_base=SANDBOX_RPC_BASE)
  new_wave = ''
  bug_id = wavelet.wave_id + '||' + str(time.time())
  props = {
      'bugId': bug_id,
      'parentWaveId': wavelet.wave_id,
      'parentWaveletId': wavelet.wavelet_id,
      'priority': priority,
      'status': status,
      'assignee': event.modified_by or 'Unknown'
  }

  for start, end in todo:
    blip.range(start, end).clear_annotation(ROBOT_KEY)
    new_participants = list(wavelet.participants)[:]
    new_participants.remove(ROBOT_ID)
    selected = blip.range(start, end).value()
    new_wave = bug_robot.new_wave(wavelet.domain,
                                  new_participants,
                                  wavelet.serialize(),
                                  submit=True)
    new_blip = new_wave.root_blip
    props['mytitle'] = 'Issue: ' + selected
    new_blip.append_markup('<b>Issue: ' + selected + '</b> ( '
                           '<a style="float:right" href="#restored:wave:' +
                           wavelet.wave_id.replace('+', '%252B', 1) +
                           '">Reference wave</a> ) ')
    new_blip.append(' \n ');

    # Update tags of current wave.
    UpdateTags(new_wave, status, type, assignee, priority)
    new_blip.append(element.Gadget(GADGET_URL, props))
    new_blip.append('\n[Add Description here]')
    bug_robot.submit(new_wave)
    link_text = ''.join([selected, msgtext])
    blip.range(start, end).replace(link_text)
    blip.range(start, end).annotate('link/wave', new_wave.wave_id)
    bug_start = end + 1
    bug_end = start + len(link_text)
    blip.range(bug_start, bug_end).annotate(BUG_KEY, bug_id)

  if new_wave == '':
    props['mytitle'] = 'Issue: '
    UpdateTags(wavelet, status, type, assignee, priority)
    new_blip = wavelet.root_blip
    new_blip.append_markup('<b>Issue: [ Set title here ]</b> ')
    new_blip.append(' \n ');
    new_blip.append(element.Gadget(GADGET_URL, props))
    new_blip.append('\n[Add Description here]')

def UpdateTags(wavelet, status, bugtype, assignee, priority):
  logging.error('updatetages:-' + status + ':' + bugtype + ':' + assignee + ':' + priority)
  if str(status) != '-1':
    wavelet.tags.append('Status=' + status)
  if str(bugtype) != '-1':
    wavelet.tags.append('Type=' + bugtype)
  if str(assignee) != '-1':
    wavelet.tags.append('Assignee=' + assignee)
  if str(priority) != '-1':
    wavelet.tags.append('Priority=' + priority)

def OnGadgetStateChanged(event, wavelet):
  """Callback function for any change in gadget state."""
  logging.error('state changed')
  blip = event.blip
  gadget = blip.first(element.Gadget, url=GADGET_URL)
  tag_list = wavelet.tags.serialize()
  logging.error(tag_list)
  for tag in tag_list:
    wavelet.tags.remove(tag)
  UpdateTags(wavelet,
             gadget.status,
             gadget.type,
             gadget.assignee,
             gadget.priority)

  logging.error(wavelet.tags.serialize())
  wave_id = gadget.parentWaveId
  wavelet_id = gadget.parentWaveletId
  bug_id = gadget.bugId
  participant_id = gadget.assignee
  bug_robot.setup_oauth(CONSUMER_KEY,
                        CONSUMER_SECRET,
                       server_rpc_base='http://sandbox.gmodules.com/api/rpc')
  parent_wavelet = bug_robot.fetch_wavelet(wave_id, wavelet_id)
  logging.error('parent waveid: ')
  logging.error(parent_wavelet)
  if str(participant_id) != '-1':
    AddParticipant(wavelet, participant_id)
  parent_status = GetBugStatus(gadget.assignee, gadget.status)
  UpdateParentWave(parent_wavelet, bug_id, parent_status)


def AddParticipant(wavelet, participant_id):
  participants = wavelet.participants
  if not participants.__contains__(participant_id):
    participants.add(participant_id.encode('utf-8'))


def GetDisplayMessage(gadget):
  return ''.join(['\nTitle=', gadget.title,
                  '\nStatus=', gadget.status,
                  '\nType=', gadget.type,
                  '\nSAssignee=', gadget.assignee,
                  '\nPriority=', gadget.priority])


def GetBugStatus(assignee, status):
  msg = ''
  if str(assignee) != '-1':
    msg = ' (Assigned: ' + assignee

  if str(status) != '-1':
    if msg == '':
      msg = ' ('
    else:
      msg = msg + ', '
    msg = msg + 'Status: ' + status + ') '

  """Get bug status text to display in parent wave."""
  return msg

def UpdateParentWave(parent_wavelet, bug_id, status):
  """Update reference wave."""
  len_status = len(status)
  for blip_id in parent_wavelet.blips:
    blip = parent_wavelet.blips[blip_id]
    todo = []
    for ann in blip.annotations:
      if ann.name == BUG_KEY and ann.value == bug_id:
        todo.append((ann.start, ann.end))
    for start, end in todo:
      blip.range(start, end).clear_annotation(BUG_KEY)
      blip.range(start, end).replace(status)
      blip.range(start, start + len_status).annotate(BUG_KEY, bug_id)
  bug_robot.submit(parent_wavelet)


if __name__ == '__main__':
  bug_robot = robot.Robot('Bugtracky', image_url=ICON, profile_url='')
  bug_robot.register_handler(events.WaveletSelfAdded, OnAnnotationChanged)
  bug_robot.register_handler(events.AnnotatedTextChanged,
                             OnAnnotationChanged,
                             filter=ROBOT_KEY)
  bug_robot.register_handler(events.GadgetStateChanged, OnGadgetStateChanged)
  appengine_robot_runner.run(bug_robot, debug=True)
