import machine

rtc = machine.RTC()

class BaseTimeSetter:
    def settime(self):
        pass


class NtpTimeSetter(BaseTimeSetter):
    def settime(self):
        import ntptime
        try:
            ntptime.settime()
            return True
        except Exception:
            return False


class LocalTimeSetter(BaseTimeSetter):
    def settime(self):
        try:
            with open("latestitme", "r") as f:
                import machine
                text = f.read()
                (year, month, day, weekday, hours, minutes, seconds, subseconds) = text.split(",")
                rtc.datetime((year, month, day, weekday, hours, minutes, seconds, subseconds))
            return True
        except:
            return False


# whenever we get a time, we store it into local as latest time
def get_current_time():
    (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
    with open("latesttime", "w") as f:
        f.write(",".join([str(year), str(month), str(day), str(weekday), str(hours), str(minutes), str(seconds), str(subseconds)]))
    return year, month, day, weekday, hours, minutes, seconds, subseconds


def set_time():
    time_setters = [NtpTimeSetter, LocalTimeSetter]
    for setter in time_setters:
        try:
            setter().settime()
        except :
            pass