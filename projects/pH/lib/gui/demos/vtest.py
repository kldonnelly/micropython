# vtest.py Test/demo of Dial for micro-gui

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Create SSD instance. Must be done first because of RAM use.
import hardware_setup

import urandom
import time
from cmath import rect, pi
import uasyncio as asyncio

from gui.core.ugui import Screen, ssd
from gui.core.writer import CWriter
from gui.fonts import font10
from gui.core.colors import *
# Widgets
from gui.widgets import Label, Button, CloseButton, Pointer, Dial


def fwdbutton(wri, row, col, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)
    Button(wri, row, col, height = 30, callback = fwd, fgcolor = BLACK, bgcolor = GREEN,
           text = text, shape = RECTANGLE, width = 100)


class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, font10, GREEN, BLACK, verbose=False)
        Label(wri, 2, 2, 'Ensure back refreshes properly')
        CloseButton(wri)


# Update a pointer with a vector. Change pointer color dependent on magnitude.
def vset(ptr, v):
    mag = abs(v)
    if mag < 0.3:
        ptr.value(v, BLUE)
    elif mag < 0.7:
        ptr.value(v, GREEN)
    else:
        ptr.value(v, RED)

def get_vec():  # Return a random vector
    mag = urandom.getrandbits(16) / 2**16  # 0..1 (well, almost 1)
    phi = pi * urandom.getrandbits(16) / 2**15  # 0..2*pi
    return rect(mag, phi)

async def ptr_test(dial):
    ptr0 = Pointer(dial)
    ptr1 = Pointer(dial)
    steps = 20  # No. of interpolation steps
    while True:
        dv0 = (get_vec() - ptr0.value()) / steps  # Interpolation vectors
        dv1 = (get_vec() - ptr1.value()) / steps
        for _ in range(steps):
            vset(ptr0, ptr0.value() + dv0)
            vset(ptr1, ptr1.value() + dv1)
            await asyncio.sleep_ms(200)

# Analog clock demo.
async def aclock(dial, lbldate, lbltim):
    uv = lambda phi : rect(1, phi)  # Return a unit vector of phase phi
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December')

    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths. Position at top.
    mstart = 0 + 1j
    sstart = 0 + 1j 

    while True:
        t = time.localtime()
        # Maths rotates vectors counterclockwise, hence - signs.
        hrs.value(hstart * uv(-t[3] * pi/6 - t[4] * pi / 360), CYAN)
        mins.value(mstart * uv(-t[4] * pi/30), CYAN)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        lbldate.value('{} {} {} {}'.format(days[t[6]], t[2], months[t[1] - 1], t[0]))
        await asyncio.sleep(1)

class VScreen(Screen):
    def __init__(self):
        super().__init__()
        labels = {'bdcolor' : RED,
                  'fgcolor' : WHITE,
                  'bgcolor' : DARKGREEN,
                  }

        wri = CWriter(ssd, font10, GREEN, BLACK, verbose=False)

        fwdbutton(wri, 200, 2, BackScreen, 'Forward')
        CloseButton(wri)
        # Set up random vector display with two pointers
        dial = Dial(wri, 2, 2, height = 100, ticks = 12, fgcolor = YELLOW, style=Dial.COMPASS)
        self.reg_task(ptr_test(dial))
        # Set up clock display: instantiate labels
        gap = 4
        lbldate = Label(wri, dial.mrow + gap, 2, 200, **labels)
        lbltim = Label(wri, lbldate.mrow + gap, 2, 80, **labels)
        dial = Dial(wri, 2, 120, height = 100, ticks = 12, fgcolor = GREEN, pip = GREEN)
        self.reg_task(aclock(dial, lbldate, lbltim))

def test():
    if ssd.height < 240 or ssd.width < 320:
        print(' This test requires a display of at least 320x240 pixels.')
    else:
        print('Testing micro-gui...')
        Screen.change(VScreen)

test()
