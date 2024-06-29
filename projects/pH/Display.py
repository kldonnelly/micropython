from hardware_setup import ssd  # Create a display instance
from gui.core.ugui import Screen
from gui.core.writer import CWriter
from gui.core.colors import *

from gui.widgets import Label, CloseButton
import gui.fonts.freesans20 as freesans20
import gui.fonts.arial35 as arial35
from observer import Subject, Observer
from log import Log
from observer_analog import AnalogPins
import uasyncio as asyncio
import socket
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral

udp = None


def advertise():
    global udp
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    udp.setsockopt(socket.SOL_SOCKET,  socket.SO_REUSEADDR, 1)
   # udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.settimeout(0.2)
   

async def run(subject):  
    port = 37020
    count = 0
    print(port)
    while True:
        await asyncio.sleep_ms(200)
        subject.update()
        count += 1
        if udp and count > 40:
            udp.sendto(bytes("test", "utf-8"), ('192.168.1.255', port))
            count = 0


class BaseScreen(Screen):
        
    ble = bluetooth.BLE() 
    p = BLESimplePeripheral(ble)

    def __init__(self):
       
        super().__init__()
        wri = CWriter(ssd, arial35, GREEN, BLACK, verbose=False)
        self.lbl1 = Label(wri, 2, 2, 'Hello world!')
        self.lbl2 = Label(wri, 40, 2, 'Hello world!')
        self.lbl3 = Label(wri, 80, 2, 'Hello world!')
        self.ao = analog_observer(self)
        _sa = AnalogPins([36, 39])
        _sa.attach(self.ao)
       # self.sa.attach(self.p.ao)
        self.reg_task(run(_sa))
        CloseButton(wri)


class analog_observer(Observer):

    def __init__(self, parent: BaseScreen):
        self.parent = parent

    def update(self, subject: Subject) -> None:
        try:
            self.parent.lbl1.value(str(subject._values[0]/1000))
            self.parent.lbl2.value(str(subject._values[1]/1000))
            mv = subject._values[1]-subject._values[0]
            self.parent.lbl3.value(str(mv/1000))
        except OSError as e:
            Log(1, e)


def start():
   # advertise()
 
    Screen.change(BaseScreen)

