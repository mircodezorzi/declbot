import json
import requests
import threading
import re
import operator

from handle import Handle

class Puller:

  def __init__(self):
    self.session     = requests.Session()

    self.updates = []

    self.callback_data = []
    self.callbacks = []

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
      self.update()
      for i in self.updates:
        for command in commands:
          if re.match('/{}({})?'.format(command[0], self.bot_handle), i.get('text')):
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
