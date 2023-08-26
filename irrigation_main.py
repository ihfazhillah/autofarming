import time

import machine
from machine import Pin, ADC, RTC
import network
import ntptime
import settings
from umqtt.simple import MQTTClient



def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(settings.WIFI_USERNAME, settings.WIFI_PASSWORD)

    while not wlan.isconnected():
        print("waiting for connection....")
        time.sleep(1)

    ntptime.settime()


def callbacks(topic, msg):
    decoded_topic = topic.decode("utf-8")
    decoded_msg = msg.decode("utf-8")

    def run_feeding(msg):
        run_feed()

    topic_map = {
        f"controller/{settings.CONTROLLER_TOKEN}/run-feed": run_feeding,
        f"controller/{settings.CONTROLLER_TOKEN}/set-mixer-length": set_mixer_length,
        f"controller/{settings.CONTROLLER_TOKEN}/set-pump-length": set_pump_length,
        f"controller/{settings.CONTROLLER_TOKEN}/set-schedule-1": set_schedule_1,
        f"controller/{settings.CONTROLLER_TOKEN}/set-schedule-2": set_schedule_2,
        f"controller/{settings.CONTROLLER_TOKEN}/set-schedule-3": set_schedule_3,
    }

    for registered_topic, cb in topic_map.items():
        if decoded_topic == registered_topic:
            cb(decoded_msg)


def mqtt_connect():
    client = MQTTClient("kolam lele", settings.MQTT_HOST, settings.MQTT_PORT, settings.MQTT_USER, settings.MQTT_PASSWORD, keepalive=3600)
    client.set_callback(callbacks)
    client.connect()
    return client


def reconnect():
    print("something bad happen")
    time.sleep(5)
    machine.reset()


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
        return 60


def set_pump_length(value):
    with open("pump_length", "w") as f:
        f.write(str(value))


schedules = {
    "schedule-1": "8:00",
    "schedule-2": "16:00",
    "schedule-3": "22:00",
}


def set_schedule_1(value):
    with open("schedule-1", "w") as f:
        f.write(value)

    get_schedules()

def set_schedule_2(value):
    with open("schedule-2", "w") as f:
        f.write(value)

    get_schedules()

def set_schedule_3(value):
    with open("schedule-3", "w") as f:
        f.write(value)
    get_schedules()

def get_schedules():
    """
    Updates schedules from local
    """
    global  schedules
    for fname, _ in schedules:
        with open(fname, "r") as f:
            schedules[fname] = f.read()



v_meter = VoltMeter(26)
pump = Pin(0, Pin.OUT, value=1)
mixer = Pin(1, Pin.OUT, value=1)
led = Pin("LED", Pin.OUT)

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


def run_feed(schedule=None):
    global feeding_run

    if feeding_run:
        return

    try:
        if schedule:
            client.publish(f"place/{settings.PLACE_ID}/controller/{settings.CONTROLLER_TOKEN}/feeding".encode(), schedule.split("-")[1])
        else:
            client.publish(f"place/{settings.PLACE_ID}/controller/{settings.CONTROLLER_TOKEN}/feeding".encode(), "")

        print(settings.PLACE_ID)
        print(settings.CONTROLLER_TOKEN)
        print("running feeding machine")
        feeding_run = True
        run_mixer()
        run_pump()

    finally:
        feeding_run = False


def on_btn_pressed(p):
    run_feed()


latest_time = time.time()
def notify_battery(client):
    global latest_time

    if time.time() - latest_time > 60 * 10:
        client.publish(f"controller/{settings.CONTROLLER_TOKEN}/{settings.BATTERY_DEVICE_ID}".encode(), str(v_meter.read()))
        latest_time = time.time()




connect()
try:
    client = mqtt_connect()
    led.on()
except OSError:
    reconnect()

# btn.irq(handler=on_btn_pressed, trigger=Pin.IRQ_RISING)

rtc = RTC()

while True:
    try:
        client.subscribe("#")
        (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()

        for schedule, tm in schedules.items():
            s_hour, s_minute = tm.split(":")

            if int(s_hour) - settings.TZ_DELTA == hours and int(s_minute) == minutes:
                print(f"running schedule {schedule}")
                run_feed(schedule)

        notify_battery(client)
        time.sleep(1)
    except OSError:
        reconnect()