import pickle
from tasks.sanitizer import Sanitizer
from tasks.median_15_seconds import Median15Seconds

class Server:
    def __init__(self, channel, queue, realtimedb, timezone=None):
        self.channel = channel
        self.queue = queue
        self.realtimedb = realtimedb
        self.timezone = timezone
        tasks = [
            Median15Seconds(self.realtimedb, self.timezone),
            Sanitizer(self.realtimedb, self.timezone),
        ]
        for t in tasks:
            t.start()

    def on_raw_data(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag = method.delivery_tag)
        self.process(body)

    def process(self, data):
        event = pickle.loads(data)

        id = "%s_%s" % (event.server_id, event.event_key)

        if not id in self.realtimedb:
            chart = {
                "_id": id,
                "server_id": event.server_id,
                "key": event.event_key,
                "type": "metric"
            }
            self.realtimedb[id] = chart

        entry = {
            "metric": id,
            "value": event.value,
            "type": "data",
            "when": event.when
        }

        self.realtimedb.save(entry)
        #print(entry)
