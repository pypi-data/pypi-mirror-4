from datetime import datetime
import pickle
import socket
from niice_client.event import Event

class Client:
    def __init__(self, channel, queue, server_id=None, timezone=None):
        self.channel = channel
        self.queue = queue
        self.server_id = server_id
        self.timezone = timezone

    def __publish(self, event):
        message = pickle.dumps(event)
        self.channel.queue_declare(queue=self.queue, durable=True)

        self.channel.basic_publish(exchange="",
            routing_key=self.queue,
            body=message)

    def send_event(self, event_key, value, server_id=None, when=None):
        if not server_id:
            if self.server_id:
                server_id = self.server_id
            else:
                server_id = socket.gethostname()

        if not when:
            when = datetime.now(tz=self.timezone)

        e = Event(server_id, event_key, value, when)
        self.__publish(e)
