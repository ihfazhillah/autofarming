# we use 1-index here
from irrigation.time_helper import get_current_time

default_schedules = [
    "8:00;feeding",
    "16:00;feeding",
    "22:00;feeding",
]


def get_schedules():
    print("get schedules")
    try:
        with open("schedules", "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines]
    except OSError:
        print("error")
        return default_schedules


def set_schedule(index, time, fn_name):
    schedules = get_schedules()
    try:
        schedules[index - 1] = ";".join([time, fn_name])
    except IndexError:
        return False

    with open("schedules", "w") as f:
        f.write("\n".join(schedules))

    return True


class Schedule:
    def __init__(self, notifier, settings):
        self.handlers = {}
        self.notifier = notifier
        self.settings = settings

    def get_schedules(self):
        return get_schedules()

    def set_schedule(self, index, time, fn_name):
        try:
            assert self.handlers[fn_name] is not None
            return set_schedule(index, time, fn_name)
        except KeyError:
            return False
        except AssertionError:
            return False

    def add_handler(self, fn_name, fn):
        self.handlers[fn_name] = fn

    def tick(self):
        schedules = self.get_schedules()

        (year, month, day, weekday, hours, minutes, seconds, subseconds) = get_current_time()
        print(f"{day}/{month}/{year} {hours}:{minutes}")
        for s_index, schedule in enumerate(schedules):
            tm, fn_name = schedule.split(";")
            s_hour, s_minute = tm.split(":")
            if int(s_hour) - self.settings.TZ_DELTA == hours and int(s_minute) == minutes:
                self.handlers[fn_name]()
                self.notifier.notify(s_index + 1, fn_name)