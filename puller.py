import json
import requests
import threading
import re

from handle import Handle
from config import config

class Puller:

  token       = config['token']
  bot_handle  = config['bot_handle']

  def __init__(self):
    self.session     = requests.Session()

    self.updates = []

    self.callback_data = []
    self.callbacks = []
    self.callbacks_recv = {}

  def __enter__(self):
    with open('/home/mirco/.cache/telegram', 'r') as f:
      self.last_update = int(f.read())
    return self

  def __exit__(self, type, value, traceback):
    with open('/home/mirco/.cache/telegram', 'w') as f:
      f.write(str(self.last_update))

  def update(self):
    r = self.session.post(
      url = f'https://api.telegram.org/bot{self.token}/getUpdates?offset={self.last_update}))',
    ).json()

    if len(r['result']):
      self.last_update = r['result'][-1]['update_id'] + 1

    for i in r['result']:
      if i.get('message'):
        self.updates.append(i['message'])
      elif i.get('callback_query'):
        self.callback_data.append(i['callback_query'])

  def execute(self, commands):
    while True:
      try:
        self.update()
      except Exception as e:
        print(e)
      for i in self.updates:
        for k in self.callbacks_recv.keys():
          if self.callbacks_recv[k] and i['chat']['id'] == self.callbacks_recv[k][0]:
            self.callbacks_recv[k][1](self.callbacks_recv[k][2])
        for command in commands:
          if re.match('/{}({})?'.format(command[0], self.bot_handle), i.get('text', '')) or re.match('/{}({})?'.format(command[0], self.bot_handle), i.get('caption', '')):
            try:
              threading.Thread(target=command[1], args=(Handle(i['chat']['id'], self), i)).start()
            except Exception as e:
              break
        del self.updates[0]
      for c in self.callback_data:
        i = 0
        while i < len(self.callbacks):
          for callback in self.callbacks[i]:
            if callback[0] == c['data']:
              threading.Thread(target=callback[1], args=(callback[2],)).start()
              del self.callbacks[i]
              i -= 1
              break
          i += 1
        del self.callback_data[0]
