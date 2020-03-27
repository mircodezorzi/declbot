#!/usr/bin/env python3
#
from puller import Puller

def schedule(h, message):
  h.send('hello',
    [
      [
        ('upcoming', lambda h: h.edit('upcoming', [[ ( 'back', lambda h: h.restore() ) ]] ) ),
        ('schedule', lambda h: h.edit('schedule') )],

      [ ('settings', lambda h: h.edit('settings') )                                        ],
    ]
  )

commands = {
  ( 'schedule', schedule ),
}

with Puller() as p:
  p.execute(commands)
