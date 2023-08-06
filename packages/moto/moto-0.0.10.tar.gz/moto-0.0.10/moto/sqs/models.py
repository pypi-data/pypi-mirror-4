import base64
import md5

from moto.core import BaseBackend
from moto.core.utils import camelcase_to_underscores, get_random_message_id
from .utils import generate_receipt_handle


class Message(object):
    def __init__(self, message_id, body):
        self.id = message_id
        self._body = body
        self.receipt_handle = generate_receipt_handle()

    @property
    def md5(self):
        body_md5 = md5.new()
        body_md5.update(self.body)
        return body_md5.hexdigest()

    @property
    def body(self):
        # SQS Message bodies are base64 encoded by default
        return base64.b64encode(self._body)


class Queue(object):
    camelcase_attributes = ['VisibilityTimeout', 'ApproximateNumberOfMessages']

    def __init__(self, name, visibility_timeout):
        self.name = name
        self.visibility_timeout = visibility_timeout or 30
        self.messages = []

    @property
    def attributes(self):
        result = {}
        for attribute in self.camelcase_attributes:
            result[attribute] = getattr(self, camelcase_to_underscores(attribute))
        return result

    @property
    def approximate_number_of_messages(self):
        return len(self.messages)


class SQSBackend(BaseBackend):

    def __init__(self):
        self.queues = {}
        super(SQSBackend, self).__init__()

    def create_queue(self, name, visibility_timeout):
        queue = Queue(name, visibility_timeout)
        self.queues[name] = queue
        return queue

    def list_queues(self):
        return self.queues.values()

    def get_queue(self, queue_name):
        return self.queues[queue_name]

    def delete_queue(self, queue_name):
        if queue_name in self.queues:
            return self.queues.pop(queue_name)
        return False

    def set_queue_attribute(self, queue_name, key, value):
        queue = self.get_queue(queue_name)
        setattr(queue, key, value)
        return queue

    def send_message(self, queue_name, message_body, delay_seconds=None):
        # TODO impemented delay_seconds
        queue = self.get_queue(queue_name)
        message_id = get_random_message_id()
        message = Message(message_id, message_body)
        queue.messages.append(message)
        return message

    def receive_messages(self, queue_name, count):
        queue = self.get_queue(queue_name)
        result = []
        for index in range(count):
            if queue.messages:
                result.append(queue.messages.pop(0))
        return result

    def delete_message(self, queue_name, receipt_handle):
        queue = self.get_queue(queue_name)
        new_messages = [
            message for message in queue.messages
            if message.receipt_handle != receipt_handle
        ]
        queue.message = new_messages


sqs_backend = SQSBackend()
