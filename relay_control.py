from machine import Pin


# dont forget to make default value is 1 (1 is off, 0 is on)
gate_8 = Pin(1, Pin.OUT, value=1)

gate_8.on()
# gate_8.o`f()off