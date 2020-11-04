```python
#!/usr/bin/env python3

import os

from client import Client
client = Client()

@client.command(cs = [ 'tex' ], description = 'generate image given latex code')
def tex(h, c):
  tmp_file = 'file.png'
  text = ' '.join(c['text'].split(' ')[1:])
  with open('file.tex', 'w') as f:
    f.write(f'\\documentclass[border={{20pt 20pt 20pt 20pt}}]{{standalone}}\\begin{{document}}${text}$\\end{{document}}')
  os.system('pdflatex -interaction nonstopmode -file-line-error file.tex')
  os.system('convert -density 300 file.pdf -quality 90 file.png')
  h.send_image(open(tmp_file, 'rb').read())

@client.command(cs = [ 'dashboard' ], description = 'dashboard')
def dashboard(h, c):
  h.send('Dashboard', [
    [
        ('a', 'a_callback'),
        ('b', lambda x: print('b')),
    ],
    [
        ('c', lambda x: print('c')),
    ]
  ])a

@client.callback(cs = 'a_callback')
def a_callback(h, c):
  h.edit('something else')

client.run()
```
