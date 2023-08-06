# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase
from random import choice


STATUS = [
    "You wanna piece of me, boy?",
    "Ready to roll out!",
    "Can I take your order?",
    "SCV good to go, sir.",
    "Alright! Bring it on!",
]

MESSAGES = [
    "I am ready.",
    "Direct my wrath.",
    "State your will.",
    "Your command?",
    "What would you ask of me?",
    "I hunger for battle...",
    "I hear you.",
    "How may I help?",
    "Your will?",
    "Hmm?",
    "You address me?",
    "Ready for battle.",
    "May I be of service?",
    "I stand ready.",
    "Yes?",
    "Awaiting instructions.",
    "Input command.",
    "Your thoughts...?",
    "Standing by.",
    "I'm here.",
    "What now...",
    "I'm waitin' on you!",
    "All crews reporting.",
    "Good day, commander.",
    "Go ahead HQ.",
    "You got my attention.",
    "Yes sir?",
    "Reportin' for duty.",
]

class StatusResponder(Responder):
    def name(self):
        return 'status'

    # def on_start(self, consumer):
    #     return "%s" % choice(STATUS)

    def generate(self, request):
        """
        usage: status
        return a random status message
        """
        return "%s" % choice(MESSAGES)

class TestStatusResponder(BaseTestCase):
    def setUp(self):
        self.responder = StatusResponder()

    def test_support(self):
        self.assertTrue(self.responder.support("status"))
        self.assertFalse(self.responder.support("fuu"))

    def test_valid(self):
        self.assertIsNotNone(self.generate("status"))
