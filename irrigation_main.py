import time

from machine import Pin, ADC, RTC
import network
import ntptime

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("sakkuun", "")

while not wlan.isconnected():
    print("waiting for connection....")
    time.sleep(1)

print(wlan.ifconfig())
print(time.localtime())
print(time.time())
ntptime.settime()
print(time.localtime())
print(time.time())
class VoltMeter:
    def __init__(self, pin):
        self.pin = pin
        self.meter = ADC(pin)

    def read(self):
        adc_read = self.meter.read_u16() / 65535 * 3.3
        return round(adc_read * (10 + 2.2) / 2.2, 2)


def get_mixer_length():
    try:
        with open("mixer_length", "r") as f:
            return int(f.read())
    except OSError:
        return 60


def set_mixer_length(value):
    with open("mixer_length", "w") as f:
        f.write(str(value))


def get_pump_length():
    try:
        with open("pump_length", "r") as f:
            return int(f.read())
    except OSError:
        return 15


def set_pump_length(value):
    with open("pump_length", "w") as f:
        f.write(str(value))


v_meter = VoltMeter(26)
pump = Pin(0, Pin.OUT, value=1)
mixer = Pin(1, Pin.OUT, value=1)
btn = Pin(2, Pin.IN, Pin.PULL_DOWN)

feeding_run = False
def run_pump():
    length = get_pump_length()
    pump.value(0)
    time.sleep(length)
    pump.value(1)


def run_mixer():
    length = get_mixer_length()
    mixer.value(0)
    time.sleep(length)
    mixer.value(1)


def on_btn_pressed(p):
    global feeding_run

    if feeding_run:
        return

    try:
        feeding_run = True
        run_mixer()
        run_pump()
    finally:
        feeding_run = False


btn.irq(handler=on_btn_pressed, trigger=Pin.IRQ_RISING)

rtc = RTC()
while True:
    print(v_meter.read())
    time.sleep(1)
    alarm = rtc.alarm(time=60 * 10, repeat=True)
    rtc.irq(alarm, handler=lambda a: print("alarm hello world"))