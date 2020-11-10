#!/usr/bin/env python3

import json
import requests
import threading
import re
import functools
import os
import uuid

from handle  import Handle
from worker  import Queue
from config  import config

class Client:

  token       = config['token']
  bot_handle  = config['bot_handle']

  def __init__(self):
    self.session = requests.Session()
    self.offset = 0

    self.message_queue = []

    self.callbacks = {
      'keys': {},
      'functions': {},
    }

    self.commands = {
      'keys': {},
      'functions': {},
    }

    self.worker = Queue(5)

    # Automatically register /help command
    @self.command(cs = [ 'help' ], description = 'Show this message')
    def help(h, c):
      s = ''
      for k, v in self.commands['functions'].items():
        s += ' '.join(v['commands']) + ' ' + v['description'] + '\n'
      h.send(s)

  def command(self, cs, description):
    def _decorator(f):
      uid = uuid.uuid1()
      self.commands['functions'][uid] = {
        'callback': f,
        'commands': ['/' + c for c in cs],
        'description': description
      }
      for c in cs:
        self.commands['keys']['/' + c] = uid
        self.commands['keys']['/' + c + self.bot_handle] = uid

    return _decorator

  def callback(self, cs):
    def _decorator(f):
      uid = uuid.uuid1()
      self.callbacks['functions'][uid] = {
        'callback': f,
        'commands': cs,
      }
      self.callbacks['keys'][cs] = uid
    return _decorator

  def run(self):
    self._load()
    self._run()
    self._save()

  def _load(self):
    if os.path.exists('/tmp/save'):
      with open('/tmp/save', 'r') as f:
        state = json.load(f)
        self.offset = int(state.get('offset', 0))
    else:
      self.offset = 0

  def _save(self):
    with open('/tmp/save', 'w') as f:
      state = {}
      state['offset'] = self.offset
      json.dump(state, f)

  def _update(self):
    r = self.session.post(
      url = f'https://api.telegram.org/bot{self.token}/getUpdates?offset={self.offset}').json()

    if len(r['result']):
      self.offset = r['result'][-1]['update_id'] + 1

    for i in r['result']:
      self.message_queue.append(i)

  def _run(self):
    while True:
      self._update()
      for i in self.message_queue:
        if i.get('message'):
          i = i['message']
          arg = i.get('text', '').split(' ')[0]
          if not arg: continue
          key = self.commands['keys'].get(arg, None)
          if key:
            self.worker.push(self.commands['functions'][key]['callback'], Handle(i['chat']['id'], None), i)
        elif i.get('callback_query'):
          i = i['callback_query']
          key = self.callbacks['keys'].get(i['data'], None)
          if key:
            self.worker.push(self.callbacks['functions'][key]['callback'], Handle(i['message']['chat']['id'], None), i)
        self.message_queue.pop(0)
