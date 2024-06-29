from observer import Subject, Observer
from log import Log
import pyvesc
from pyvesc.VESC.messages import GetValues_mp
from UartShared import UartObserver, UartShared


class VESC(Subject):

    response = None
    _uart = None
    _get_values_msg = None
    m_get_values_pkt = None
    _count = 0
    _buffer = None
    _observers: List[Observer] = []
    uo = None
   
  
    def __init__(self, uart: UartShared):
        self._uart = uart
        self._count = 0
        self._get_values_msg = GetValues_mp()
        self.m_get_values_pkt = pyvesc.encode_request_mp(self._get_values_msg)
        self.uo = self.uart_observer(self, 0, self.m_get_values_pkt, 61)
        self._uart.attach(self.uo)
        #self.vo = self.vesc_observer(self, uart)
        # self.tim1 = Timer(0)
        # self.tim1.init(period=200, mode=Timer.PERIODIC, callback=self.update)
        Log(self.m_get_values_pkt)

    def attach(self, observer: Observer) -> None:
        Log("VESC: Attached an observer.")
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        """
        Trigger an update in each subscriber.
        """

        Log(4, "Subject: Notifying observers...")
        for observer in self._observers:
            observer.update(self.response)

    def update(self) -> int:
        res = 1
        if self._count < 1:
            if self._uart.write(self.uo) < 0:
                Log(4, "network connected")
                self.response = "Networked"
                self.notify()

            self._count = 10


        len = self._uart.read(self.uo)

        if len > 0:
            self._count = 0
        elif len < 0:
             Log(4, "network connected")
        else:
            self._count -= 1
            res = 0

        return res     

    class uart_observer(UartObserver):

        def __init__(self, parent, priority, write_bytes, read_length) -> None:
            self.parent = parent
            super().__init__(priority, write_bytes, read_length)

        def update(self, subject: Subject) -> None:
            self.parent._buffer = subject._buffer
            try:
                (self.parent.response, consumed) = pyvesc.decode_mp(self.parent._get_values_msg, self.parent._buffer)
            except OSError:
                Log("OS Error failed to decode_mp")
            except KeyError:
                Log("keyerror")
            
            if self.parent.response:
                self.parent.notify()
                self.parent._count = 0

    


    
