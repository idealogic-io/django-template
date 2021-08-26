import pika
import json
from decimal import Decimal


class RabbitMQManager(object):

    def __init__(self):
        credentials = pika.PlainCredentials('admin', 'mypass')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                'django_boilerplate-rabbit', 5672,
                'vhost',
                credentials
            )
        )
        self.channel = self.connection.channel()

    def __enter__(self):
        return self.channel

    def __exit__(self, type, value, traceback):
        self.connection.close()


class FakeFloat(float):

    def __init__(self, value):
        self._value = value
        super().__init__()

    def __repr__(self):
        return str(self._value)


def default_encode(o):
    if isinstance(o, Decimal):
        return FakeFloat(o)
    raise TypeError(repr(o) + " is not JSON serializable")


def send_socket_message(room, event, content):
    payload = {
        'room': room,
        'event': event,
        'content': content
    }
    with RabbitMQManager() as rabbit_handler:
        rabbit_handler.basic_publish(
            exchange='',
            routing_key='payload',
            body=json.dumps(payload, default=default_encode)
        )


def broadcast_socket_message(rooms, event, content):
    payload = {
        'rooms': rooms,
        'event': event,
        'content': content
    }
    with RabbitMQManager() as rabbit_handler:
        rabbit_handler.basic_publish(
            exchange='',
            routing_key='broadcast',
            body=json.dumps(payload, default=default_encode)
        )
