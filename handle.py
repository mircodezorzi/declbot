import functools
import operator
import re
import requests
import time
import json

from config import config

class Handle:

  token       = config['token']
  bot_handle  = config['bot_handle']

  def __init__(self, chat_id, parent):
    self.session = requests.Session()

    self.chat_id     = chat_id
    self.message_id  = ''

    self.parent = parent
    self.hashes = []

    self.state = []

  def _request(self, endpoint, args = {}, **kargs):
    default = {
      'chat_id': self.chat_id,
      'parse_mode': 'html',
      'disable_web_page_preview': True,
    }

    return self.session.post(
      url = f'https://api.telegram.org/bot{self.token}/{endpoint}',
      data = {
        **default,
        **args
      },
      **kargs,
    ).json()['result']

  def send_image(self, image):
    m = self._request(
      'sendPhoto',
      files={ "photo": image }
    )
    self.message_id = m['message_id']

  def send(self, text, keyboard = []):
    hash = str(time.time())

    if keyboard != []:
      self.state.append({
        'text': text,
        'keyboard': keyboard,
      })

    def get_key(k):
      return {
        'text': k[0],
        'callback_data': k[1] if callable(k[1]) else k[0]
    }

    m = self._request(
      'sendMessage', {
        'text': text,
        'reply_markup': json.dumps({
          'inline_keyboard': [[ get_key(key) for key in row] for row in keyboard]
        })
      }
    )

    self.message_id = m['message_id']

    if keyboard != []:
      self.parent.callbacks.append(functools.reduce(operator.concat, [[ (k[0] + hash, k[1], self) for k in key] for key in keyboard]))

  def edit(self, text, keyboard = []):
    hash = str(time.time())

    if keyboard != []:
      self.state.append({
        'text': text,
        'keyboard': keyboard,
      })

    m = self._request(
      'editMessageText', {
        'text': text,
        'message_id': self.message_id,
        'reply_markup': json.dumps({
          'inline_keyboard': [[ { 'text': k[0], 'callback_data': k[0] + hash } for k in key] for key in keyboard]
        }),
      }
    )

    if keyboard != []:
      self.parent.callbacks.append(functools.reduce(operator.concat, [[ (k[0] + hash, k[1], self) for k in key] for key in keyboard]))

  def recv(self, callback):
    hash = str(time.time())
    self.hashes.append(hash)

    def anon(*args, **kargs):
      callback(*args, **kargs)
      if len(self.hashes):
        self.parent.callbacks_recv[self.hashes.pop()] = None

    self.parent.callbacks_recv[hash] = (self.chat_id, anon, self)

  def restore(self, n):
    s = self.state.pop()
    for i in range(n):
      s = self.state.pop()
    self.edit(s['text'], keyboard = s['keyboard'])
    if len(self.hashes):
      self.parent.callbacks_recv[self.hashes.pop()] = None

  def close(self):
    self._request('deleteMessage', { 'message_id': self.message_id })
