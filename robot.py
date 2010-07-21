#!/usr/bin/python2.5
#
# Copyright 2010 Google Inc.
"""Robot that creates a wave for an issue."""

import time
import logging

from waveapi import appengine_robot_runner
from waveapi import element
from waveapi import events
from waveapi import robot
from google.appengine.ext import db
from google.appengine.api.urlfetch import DownloadError 

import common
import credentials

def OnAnnotationChanged(event, wavelet):
  """Called when the annotation changes."""
  blip = event.blip
  todo = []

  for ann in blip.annotations:
    if ann.name == common.ROBOT_KEY:
      todo.append((ann.start, ann.end))

  msgtext = ''
  assignee = event.modified_by
  msgtext = ' (Assigned: ' + event.modified_by
  status = 'New'
  if msgtext == '':
    msgtext = ' ('
  else:
    msgtext = msgtext + ', '
  msgtext = msgtext + 'Status: ' + status + ') '
  priority = '2'
  type = 'bug'

  bug_robot.setup_oauth(credentials.KEY,
                        credentials.SECRET,
                        common.GetRPCBase(wavelet.domain))
  new_wave = ''
  bug_id = wavelet.wave_id + '||' + str(time.time())
  props = {
      'bugId': bug_id,
      'parentWaveId': wavelet.wave_id,
      'parentWaveletId': wavelet.wavelet_id,
      'priority': priority,
      'status': status,
      'assignee': event.modified_by or ''
  }

  for start, end in todo:
    blip.range(start, end).clear_annotation(common.ROBOT_KEY)
    new_participants = list(wavelet.participants)[:]
    selected = blip.range(start, end).value()
    new_wave = bug_robot.new_wave(wavelet.domain,
                                  new_participants,
                                  wavelet.serialize(),
                                  submit=True)
    title = 'Issue: %s' % selected
    props['mytitle'] = title
    new_wave.title = title
    UpdateTags(new_wave, status, type, assignee, priority)

    # Add contents to blip
    new_blip = new_wave.root_blip
    new_blip.append('(Reference Wave)', bundled_annotations=[('link/wave', wavelet.wave_id)])
    new_blip.append('\n', bundled_annotations=[('link/wave', None)])
    new_blip.append(element.Gadget(common.GetGadgetUrl(), props))
    new_blip.append('\nDescription:', [('style/fontWeight', 'bold')])
    new_blip.append('\n', [])
    bug_robot.submit(new_wave)

    # Update blip in parent wave
    link_text = ''.join([selected, msgtext])
    blip.range(start, end).replace(link_text)
    blip.range(start, end).annotate('link/wave', new_wave.wave_id)
    bug_start = end + 1
    bug_end = start + len(link_text)
    blip.range(bug_start, bug_end).annotate(common.BUG_KEY, bug_id)

  if new_wave == '':
    wavelet.title = 'Issue: '
    new_blip = wavelet.root_blip
    new_blip.append(element.Gadget(common.GetGadgetUrl()))
    new_blip.append('\nDescription:', [('style/fontWeight', 'bold')])
    new_blip.append('\n', [])

def UpdateTags(wavelet, status, bugtype, assignee, priority):
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
  blip = event.blip
  gadget = blip.first(element.Gadget, url=common.GetGadgetUrl())
  tag_list = wavelet.tags.serialize()
  for tag in tag_list:
    wavelet.tags.remove(tag)
  UpdateTags(wavelet,
             gadget.status,
             gadget.get('type'),
             gadget.assignee,
             gadget.priority)

  # Add assignee to the wave
  participant_id = gadget.assignee
  if str(participant_id) != '-1':
    AddParticipant(wavelet, participant_id)

  # Attempt to update parent wave if exists
  wave_id = gadget.get('parentWaveId')
  if wave_id is None:
    return

  bug_robot.setup_oauth(credentials.KEY,
                        credentials.SECRET,
                        common.GetRPCBase(wavelet.domain))
  try:
    bug_id = gadget.get('bugId')
    wavelet_id = gadget.get('parentWaveletId')
    parent_wavelet = bug_robot.fetch_wavelet(wave_id, wavelet_id)
    parent_status = GetBugStatus(gadget.assignee, gadget.status)
    UpdateParentWave(parent_wavelet, bug_id, parent_status)
  except DownloadError:
    logging.info('Problem fetching wave %s' % wave_id)



def AddParticipant(wavelet, participant_id):
  participants = wavelet.participants
  if not participants.__contains__(participant_id):
    participants.add(participant_id.encode('utf-8'))


def GetDisplayMessage(gadget):
  return ''.join(['\nTitle=', gadget.title,
                  '\nStatus=', gadget.status,
                  '\nType=', gadget.get('type'),
                  '\nSAssignee=', gadget.assignee,
                  '\nPriority=', gadget.priority])


def GetBugStatus(assignee, status):
  """Get bug status text to display in parent wave."""
  msg = ''
  if str(assignee) != '-1':
    msg = ' (Assigned: ' + assignee

  if str(status) != '-1':
    if msg == '':
      msg = ' ('
    else:
      msg = msg + ', '
    msg = msg + 'Status: ' + status + ') '
  return msg

def UpdateParentWave(parent_wavelet, bug_id, status):
  """Update reference wave."""
  len_status = len(status)
  for blip_id in parent_wavelet.blips:
    blip = parent_wavelet.blips[blip_id]
    todo = []
    for ann in blip.annotations:
      if ann.name == common.BUG_KEY and ann.value == bug_id:
        todo.append((ann.start, ann.end))
    for start, end in todo:
      blip.range(start, end).clear_annotation(common.BUG_KEY)
      blip.range(start, end).replace(status)
      blip.range(start, start + len_status).annotate(common.BUG_KEY, bug_id)
  bug_robot.submit(parent_wavelet)


if __name__ == '__main__':
  bug_robot = robot.Robot('Bugtracky', image_url=common.GetAvatarUrl(),
                          profile_url=common.GetServer())
  bug_robot.register_handler(events.WaveletSelfAdded, OnAnnotationChanged)
  bug_robot.register_handler(events.AnnotatedTextChanged,
                             OnAnnotationChanged,
                             filter=common.ROBOT_KEY)
  bug_robot.register_handler(events.GadgetStateChanged, OnGadgetStateChanged)
  appengine_robot_runner.run(bug_robot, debug=True)
