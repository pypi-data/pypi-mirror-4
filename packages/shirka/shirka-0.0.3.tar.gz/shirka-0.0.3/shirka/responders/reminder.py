# vim: set fileencoding=utf-8 :

from shirka.responders import Responder, StreamResponse
import requests, json, re, time, threading
from shirka.consumers import BaseTestCase

class ReminderStreamResponse(StreamResponse):
    def handle(self, request, consumer):
        consumer.post("Roger that!! (reminder set)", request)

        def remind():
            consumer.post("Reminder: %s" % self.content, request)

        t = threading.Timer(self.end - time.time(), remind)
        t.run()

class ReminderResponder(Responder):

    def __init__(self):
        self.pattern = re.compile("")
        super(ReminderResponder, self).__init__()

    def name(self):
        return 'reminder'

    def generate(self, request):
        """
        usage: reminder time message
        store a reminder, time must be integer + unit : 15s or 15m. 
        valid unit: s (seconde), m (minute) and h (hour)
        """
        try:
            cmd, format, message = request.content.split(" ", 2)
        except Exception, e:
            return False
        
        end = self.get_time(format)

        if end == False:
            return False

        response = ReminderStreamResponse(message)
        response.end = end

        return response

    def get_time(self, number):
        number, format = re.match("([0-9]*)(.*)", number).groups()

        number = float(number)

        base = time.time()

        if format == 's':
            return base + number

        if format == 'm':
            return base + number * 60

        if format == 'h':
            return base + number * 3600

        return False

class TestReminderResponder(BaseTestCase):
    def setUp(self):
        self.responder = ReminderResponder()

    def test_support(self):
        self.assertTrue(self.responder.support("reminder"))
        self.assertFalse(self.responder.support("fuu"))

    def test_invalid_count(self):
        self.assertFalse(self.generate("reminder"))

    def test_invalid_time(self):
        self.assertFalse(self.generate("reminder 15j see raph about webservices"))

    def test_valid(self):
        response = self.generate("reminder 0s see raph about webservices")
        self.assertIsInstance(response, ReminderStreamResponse)
        self.assertIsNotNone(response.end)

    def test_on_start(self):
        self.assertFalse(self.responder.on_start(False))

