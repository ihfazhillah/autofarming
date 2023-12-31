from irrigation.functions import Pump, Mixer, Feed
from irrigation.mymqtt import MyMQTT
from irrigation.time_helper import set_time
from irrigation.volt_meter import VoltMeter, Battery
from irrigation.wifi import connect
from irrigation.notifier import Notifier, pop_pending_notification

import time

from machine import Pin, ADC, RTC
import settings
from umqtt.simple import MQTTClient

from irrigation.schedule import Schedule

mqtt_client = MQTTClient(
    "kolam lele",
    settings.MQTT_HOST,
    settings.MQTT_PORT,
    settings.MQTT_USER,
    settings.MQTT_PASSWORD,
    keepalive=3600
)

pump_pin = Pin(0, Pin.OUT, value=1)
pump = Pump(pump_pin)

mixer_pin = Pin(1, Pin.OUT, value=1)
mixer = Mixer(mixer_pin)

feed = Feed(pump, mixer)

def feeding_handler(msg):
    feed.run_feed()
    notifier.notify(None, "feeding")


my_mqtt = MyMQTT(mqtt_client, settings)
my_mqtt.register("run-feed", feeding_handler)
my_mqtt.register("set-mixer-length", mixer.set_length)
my_mqtt.register("set-pump-length", pump.set_length)

my_mqtt.register("control-pump", lambda msg: pump.on() if msg == "1" else pump.off())
my_mqtt.register("control-mixer", lambda msg: mixer.on() if msg == "1" else mixer.off())


v_meter = VoltMeter(ADC(Pin(26)))
battery = Battery(v_meter, my_mqtt, settings)


notifier = Notifier(my_mqtt, settings)


internal_led = Pin("LED", Pin.OUT)
no_connection_led = Pin(15, Pin.OUT)


schedule = Schedule(notifier, settings)
schedule.add_handler("feeding", feed.run_feed)


def handle_schedule(msg):
    index, time, fn_name = msg.split(";")
    schedule.set_schedule(int(index), time, fn_name)

my_mqtt.register("set-schedule", handle_schedule)

# old functions
my_mqtt.register("set-schedule-1", lambda msg: schedule.set_schedule(1, msg, "feeding"))
my_mqtt.register("set-schedule-2", lambda msg: schedule.set_schedule(2, msg, "feeding"))
my_mqtt.register("set-schedule-3", lambda msg: schedule.set_schedule(3, msg, "feeding"))


connected = connect(settings.WIFI_USERNAME, settings.WIFI_PASSWORD)


def no_connection():
    global connected

    connected = False
    no_connection_led.on()
    internal_led.off()


def has_connection():
    global connected

    connected = True
    no_connection_led.off()
    internal_led.on()


if not connected:
    no_connection()
else:
    set_time()
    has_connection()

if connected:
    try:
        my_mqtt.connect()
    except:
        no_connection()


while True:
    try:
        my_mqtt.subscribe()
    except Exception as e:
        print(f"subscribe error {e}")
        no_connection()

    try:
        schedule.tick()
    except Exception as e:
        print(f"tick error {e}")
        no_connection()

    battery.notify()

    # handle pending notifications
    # why one by one each seconds? To prevent blocking loop if
    # we have no connection
    pending_notification = pop_pending_notification()
    if pending_notification:
        idx, fn_name = pending_notification.split(";")
        notifier.notify(idx, fn_name)

    if not connected:
        connect(settings.WIFI_USERNAME, settings.WIFI_PASSWORD)
        set_time()
        try:
            my_mqtt.connect()
            has_connection()
        except:
            no_connection()

    time.sleep(1)