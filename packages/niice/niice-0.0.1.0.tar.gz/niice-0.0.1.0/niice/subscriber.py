import time
from niice_client.connection import rabbitmq_connection

class Subscriber():
    def __init__(self, callback, channel, late_ack=False):
        self.queue = rabbitmq_queue
        self.rabbitmq_host = rabbitmq_host
        self.channel = None
        self.__callback = callback
        self.__late_ack = late_ack

    def callback(self, ch, method, properties, body):
        if not self.__late_ack:
            ch.basic_ack(delivery_tag = method.delivery_tag)
        self.__callback(body)
        if self.__late_ack:
            ch.basic_ack(delivery_tag = method.delivery_tag)
        time.sleep(0.1)

    def start(self):
        self.run()

    def run(self):
        with rabbitmq_connection(self.rabbitmq_host) as channel:
            self.channel = channel
            channel.queue_declare(queue=self.queue, durable=True)
            channel.basic_consume(self.callback,
                queue=self.queue)
            channel.basic_qos(prefetch_count=1)
            channel.start_consuming()

    def stop(self):
        if self.channel:
            self.channel.stop_consuming()

