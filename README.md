``` python

def schedule(h):
  h.edit('schedule, waiting for response!', [[ _back ]])
  h.recv(lambda h: h.edit('done!'))

def dashboard(h, message):
  h.send('Dashboard',
    [
      [
        ('📆 Upcoming', lambda h: h.edit('upcoming', [[ _back ]] ) ),
        ('📌 Schedule', schedule )
      ],
      [
        ('⚙ Settings', lambda h: h.edit('settings', [[ _back ]]) )
      ],
      [ _close ]
    ]
  )

commands = {
  ( 'dashboard', dashboard ),
}

with Puller() as p:
  p.execute(commands)
```
