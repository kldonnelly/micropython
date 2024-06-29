# This example demonstrates a UART periperhal.

import bluetooth
import struct
from ble_advertising import advertising_payload
from observer import Subject, Observer
from log import Log
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_MTU_EXCHANGED = const(21)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_VOLTAGE_IO_UUID = bluetooth.UUID("26b93bf8-5051-11ee-be56-0242ac120002")
_VOLTAGE_IN = (bluetooth.UUID("26b93bf8-5051-11ee-be56-0242ac120003"),_FLAG_READ|_FLAG_NOTIFY,)
_VOLTAGE_OUT = (bluetooth.UUID("26b93bf8-5051-11ee-be56-0242ac120004"),_FLAG_WRITE|_FLAG_WRITE_NO_RESPONSE,)


_VOLTAGE_IO_SERVICE = (_VOLTAGE_IO_UUID, (_VOLTAGE_IN, _VOLTAGE_OUT, ),)


class BLESimplePeripheral:
    def __init__(self, ble, name="mpy-ph"):
        self._ble = ble
        self._ble.active(True)
        self._ble.config(mtu=500)
       
        # self._ble.config(rxbuf=512)
        self._ble.irq(self._irq)

        ((self._handle_i, self._handle_o, ), ) = self._ble.gatts_register_services((_VOLTAGE_IO_SERVICE, ))
        self._connections = set()
    
        Log("name=", name)
        self._payload = advertising_payload(name=name, services=[_VOLTAGE_IO_UUID])
        self._advertise() 
        self.ao = self.analog_observer(self)


    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            Log("New connection", conn_handle)
            self._connections.add(conn_handle)
            #self._advertise()
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            Log("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
        elif event == _IRQ_MTU_EXCHANGED:
            # ATT MTU exchange complete (either initiated by us or the remote device).
            conn_handle, mtu = data
            print("mtu="+str(data))
           
    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        Log("Starting advertising")
        try:
            self._ble.gap_advertise(interval_us, adv_data=self._payload)
        except OSError as error:
            Log(error.errno)           

    class analog_observer(Observer):

        def __init__(self, parent):
            self.parent = parent
        
        def update(self, subject: Subject) -> None:
            data = struct.pack("<ll", subject._values[0], subject._values[1])

            for conn_handle in self.parent._connections:               
                try:
                    self.parent._ble.gatts_notify(conn_handle, self.parent._handle_i, data)
                except OSError:
                    Log(1, "failed to update with gatts_notify")

    
def ble_main(sa=0):
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)
   
    if sa != 0:
        sa.attach(p.ao)

    return p

    
        


