import dateparser
import datetime
import time
import functools
import operator

import json
import pickle

import requests
import re

import subprocess
import os

class Handle:

  def __init__(self, chat_id, parent):
    self.session = requests.Session()

    self.chat_id     = chat_id
    self.message_id  = ''

    self.parent = parent

    self.state = []

  def _request(self, endpoint, args = {}, **kargs):
    default = {
      'chat_id': self.chat_id,
      'parse_mode': 'html'
    }

    return self.session.post(
      url = f'https://api.telegram.org/bot{self.token}/{endpoint}',
      data = {
        **default,
        **args
      },
      **kargs,
    ).json()['result']

  def send(self, text, keyboard = []):
    hash = str(time.time())

    if keyboard != []:
      self.state.append({
        'text': text,
        'keyboard': keyboard,
      })

    m = self._request(
      'sendMessage', {
        'text': text,
        'reply_markup': json.dumps({
          'inline_keyboard': [[ { 'text': k[0], 'callback_data': k[0] + hash }  for k in key] for key in keyboard]
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
          'inline_keyboard': [[ { 'text': k[0], 'callback_data': k[0] + hash }  for k in key] for key in keyboard]
        }),
      }
    )

    if keyboard != []:
      self.parent.callbacks.append(functools.reduce(operator.concat, [[ (k[0] + hash, k[1], self) for k in key] for key in keyboard]))

  def restore(self):
    s = self.state.pop()
    s = self.state.pop()
    self.edit(s['text'], keyboard = s['keyboard'])