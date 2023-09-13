import time


class VoltMeter:
    def __init__(self, adc):
        self.meter = adc

    def read(self):
        adc_read = self.meter.read_u16() / 65535 * 3.3
        # 2.2K resistor and 10K resistor
        return round(adc_read * (10 + 2.2) / 2.2, 2)


class Battery:
    def __init__(self, battery, client, settings):
        self.client = client
        self.battery = battery
        self.latest_time = time.time()
        self.topic = f"controller/{settings.CONTROLLER_TOKEN}/{settings.BATTERY_DEVICE_ID}"

    def notify(self):
        if time.time() - self.latest_time > 60 * 1:
            try:
                self.client.publish(self.topic, str(self.battery.read()))
            except:
                pass

            self.latest_time = time.time()

