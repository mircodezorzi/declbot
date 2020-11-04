#!/usr/bin/env python3

import subprocess
import time
import os

from client import Client
client = Client()

@client.command(
  cs = [ 'tex' ],
  description = 'generate image given latex code')
def tex(h, c):
  tmp_file = 'file.png'
  text = ' '.join(c['text'].split(' ')[1:])
  with open('file.tex', 'w') as f:
    f.write(f'\\documentclass[border={{20pt 20pt 20pt 20pt}}]{{standalone}}\\begin{{document}}${text}$\\end{{document}}')
  os.system('pdflatex -interaction nonstopmode -file-line-error file.tex')
  os.system('convert -density 300 file.pdf -quality 90 file.png')
  h.send_image(open(tmp_file, 'rb').read())
    time.sleep(1)

@client.command(
  cs = [ 'f', 'fortune' ],
  description = 'Fortune')
def fortune(h, message):
  s = subprocess.run(['fortune'], capture_output=True)
  h.send(s.stdout.decode())

client.run()
