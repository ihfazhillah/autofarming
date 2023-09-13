import time
import machine


class Pump:
    default_length = 60

    def __init__(self, pin):
        self.pin = pin

    def on(self):
        self.pin.value(0)

    def off(self):
        self.pin.value(1)

    def run(self):
        self.on()
        self.off()

    def get_length(self):
        try:
            with open("pump_length", "r") as f:
                return int(f.read())
        except OSError:
            return self.default_length

    def set_length(self, value):
        with open("pump_length", "w") as f:
            f.write(str(value))


class Mixer:
    default_length = 60

    def __init__(self, pin):
        self.pin = pin

    def on(self):
        self.pin.value(0)

    def off(self):
        self.pin.value(1)

    def run(self):
        self.on()
        self.off()

    def get_length(self):
        try:
            with open("mixer_length", "r") as f:
                return int(f.read())
        except OSError:
            return self.default_length

    def set_length(self, value):
        with open("mixer_length", "w") as f:
            f.write(str(value))


class Feed:
    def __init__(self, pump, mixer):
        self.pump = pump
        self.mixer = mixer

        self.is_running = False

    def run_feed(self):
        if self.is_running:
            return

        self.is_running = True
        self.mixer.on()

        machine.Timer(period=self.mixer.get_length(), mode=machine.Timer.ONE_SHOT, callback=lambda t: self.pump.on())

        def off(t):
            self.pump.off()
            self.mixer.off()
            self.is_running = False

        machine.Timer(period=self.mixer.get_length + self.pump.get_length(), mode=machine.Timer.ONE_SHOT, callback=off)
