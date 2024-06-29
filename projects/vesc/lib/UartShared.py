from observer import Subject, Observer
from log import Log

class UartObserver(Observer):

    def __init__(self, priority: int, write_bytes, read_length: int) -> None:

        self.priority = priority
        self.write_bytes = write_bytes
        self.read_length = read_length
        super().__init__()


class UartShared(Subject):

    _observers = []
    _buffer = []

    def large(self, arr):
        # root element varible
        max_ = arr[0]
        for ele in arr:
            if ele.priority > max_.priority:
                max_ = ele
        return max_

    def __init__(self, uart) -> None:
        self._uart = uart
        super().__init__()

    def attach(self, observer: UartObserver) -> None:
        self._observers.append(observer)
        Log("UART: Attached an observer.")
        return super().attach(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
        return super().detach(observer)

    def notify(self) -> None:
        #.read()
        max_observer: UartObserver = self.large(self._observers)
        max_observer.update(self)

        return super().notify()

    def write(self,  obs: UartObserver, bytes=[]):
        max_observer = self.large(self._observers)
        if max_observer != obs:
            return -1

        if bytes:
            obs.write_bytes = bytes

        self._uart.write(obs.write_bytes)

        return 0
   
    def read(self, obs: UartObserver) -> int:
        max_observer: UartObserver = self.large(self._observers)
        if max_observer != obs:
            return -1

        len = self._uart.any()

        if len > max_observer.read_length:
            self._buffer = self._uart.read(len)
            self.notify()

        return len
       
