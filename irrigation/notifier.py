class Notifier:
    """Schedule notifier"""
    def __init__(self, client, settings):
        self.client = client
        self.topic = f"place/{settings.PLACE_ID}/controller/{settings.CONTROLLER_TOKEN}"

    def notify(self, index=None, fn_name=None):
        topic = self.topic + f"/{fn_name}"
        idx = str(index) if index else ""

        try:
            print("publishing")
            self.client.publish(topic, idx)
        except Exception:
            print("exception in publishing")
            set_pending_notification(idx, fn_name)



def pending_notifications():
    try:
        with open("pending_notifications", "r") as f:
            return [s.strip() for s in f.readlines()]
    except OSError:
        return []


def set_pending_notification(idx, fn_name):
    notifs = pending_notifications()
    notifs.append(";".join([str(idx), fn_name]))
    with open("pending_notifications", "w") as f:
        f.writelines(notifs)


def pop_pending_notification():
    notifs = pending_notifications()
    if not notifs:
        return

    notification = notifs.pop()
    with open("pending_notifications", "r") as f:
        f.writelines(notifs)

    return notification