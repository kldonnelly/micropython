import ble_simple_peripheral
from observer_analog import AnalogPins
from machine import Timer


_sa = AnalogPins([36, 39])

ble_simple_peripheral.ble_main(_sa)

def update(t):
    _sa.update()
    # p.update()
 

tim1 = Timer(0)
tim1.init(period=500, mode=Timer.PERIODIC, callback=update)

#do_connect()


#from Display import start

# start()
#