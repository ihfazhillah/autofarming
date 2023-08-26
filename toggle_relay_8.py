from machine import Pin, ADC, RTC


pump = Pin(0, Pin.OUT, value=1)
btn = Pin(2, Pin.IN, Pin.PULL_DOWN)


def on_btn_pressed(p):
    pump.toggle()


btn.irq(handler=on_btn_pressed, trigger=Pin.IRQ_RISING)