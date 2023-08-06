from contextlib import contextmanager
import pika

class BasicConfiguration:
    def __init__(self, rabbitmq_host, rabbitmq_port, rabbitmq_queue, rabbitmq_user, rabbitmq_password, tz=None):
        self.host = rabbitmq_host
        self.port = rabbitmq_port
        self.queue = rabbitmq_queue
        self.user = rabbitmq_user
        self.password = rabbitmq_password
        self.timezone = tz

    @contextmanager
    def rabbitmq_connection(self):
        credentials = pika.credentials.PlainCredentials(self.user, self.password)
        c = pika.BlockingConnection(pika.ConnectionParameters(self.host, port=self.port, credentials=credentials))
        channel = c.channel()
        try:
            yield channel
        finally:
            if c is not None:
                c.close()