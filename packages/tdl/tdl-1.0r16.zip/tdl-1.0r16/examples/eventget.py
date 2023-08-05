#!/usr/bin/env python
"""
    An interactive example of what events are available.
"""

import sys
sys.path.insert(0, '../')

import tdl

WIDTH, HEIGHT = 80, 60

console = tdl.init(WIDTH, HEIGHT)

# the scrolling text window
textWindow = tdl.Window(console, 0, 0, WIDTH, HEIGHT-2)

# slow down the program so that the user can more clearly see the motion events
tdl.setFPS(24)

while 1:
    for event in tdl.event.get():
        if event.type == 'QUIT':
            raise SystemExit()
        elif event.type == 'MOUSEMOTION':
            # clear and print to the bottom of the console
            console.drawRect(0, HEIGHT - 1, None, None, ' ')
            console.drawStr(0, HEIGHT - 1, 'MOUSEMOTION event - pos=%i,%i cell=%i,%i motion=%i,%i cellmotion=%i,%i' % (event.pos + event.cell + event.motion + event.cellmotion))
            continue # prevent scrolling
        
        textWindow.scroll(0, -1)
        if event.type == 'KEYDOWN' or event.type == 'KEYUP':
            textWindow.drawStr(0, HEIGHT-3, '%s event - key=%.2i char=%s keyname=%s alt=%i ctrl=%i shift=%i' % (event.type.ljust(7), event.key, repr(event.char), repr(event.keyname), event.alt, event.ctrl, event.shift))
        elif event.type == 'MOUSEDOWN' or event.type == 'MOUSEUP':
            textWindow.drawStr(0, HEIGHT-3, '%s event - pos=%i,%i cell=%i,%i button=%i' % ((event.type.ljust(9),) + event.pos + event.cell + (event.button,)))
    tdl.flush()
