class MyMQTT:
    def __init__(self, client, settings):
        self.client = client
        self.settings = settings
        self.handlers = {}

        self.base_topic = f"controller/{self.settings.CONTROLLER_TOKEN}"

    def register(self, topic, fn):
        self.handlers[self.base_topic + f"/{topic}"] = fn

    def callbacks(self, topic, msg):
        decoded_topic = topic.decode("utf-8")
        decoded_msg = msg.decode("utf-8")

        for tpc, cb in self.handlers.items():
            if tpc == decoded_topic:
                cb(decoded_msg)

    def connect(self):
        self.client.set_callback(self.callbacks)
        self.client.connect()

    def subscribe(self):
        self.client.subscribe("#")

    def publish(self, topic, message):
        self.client.publish(topic.encode(), message)
