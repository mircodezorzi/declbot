#!/usr/bin/env python3

import time
import cv2

from client import Client
client = Client()

def nearest_colour(query):
    subjects = ((255, 255, 255, "⬜️"), # white
                (50,   50,  50, "⬛️"), # black
                (200,   0,   0, "🟥"), # red
                (0,   200,   0, "🟩"), # green
                (0,     0, 200, "🟦"), # blue
                (255, 165,   0, "🟧"), # orange
                (255, 255,   0, "🟨"), # yellow
                (255,   0, 255, "🟪"), # purple
                (165,  42,  42, "🟫")) # brown
    return min(subjects, key = lambda subject: sum((s - q) ** 2 for s, q in zip(subject, query)))

def render(img):
  buf = ''
  arr = np.array(img)
  for row in arr:
    for pix in row:
      pix = pix[0:3]
      buf += nearest_colour(pix)[3]
    buf += '\n'
  return buf

@client.command(cs = [ 'webcam' ], description = '')
def a(h, c):
  h.send('')
  while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (20, 20))
    h.edit(render(frame))
    time.sleep(1)

client.run()
