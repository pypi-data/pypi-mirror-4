# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase

class HelpResponder(Responder):

    def __init__(self):
        self.helps = []

    def name(self):
        return 'help'

    def on_start(self, consumer):
        for responder in consumer.responders:
            if not responder.generate.__doc__:
                continue

            help = "\n".join([("> " + line.strip()) for line in responder.generate.__doc__.split("\n")])
            self.helps.append((responder.name(), help.strip()))

        return False

    def generate(self, request):
        """
        usage: help [command]
        retrieves help information from registered responders
        """
        message = "# Help\n"

        for name, help in self.helps:
            message = "%s##%s \n%s\n---\n" % (message, name, help)
        
        return message

class FakeConsumer(object):
    def __init__(self, responders):
        self.responders = responders

class FakeResponder(Responder):
    def name(self):
        return 'fake'

    def generate(self, message):
        """
        My help message
        Look greats from here
        """
        return "salut"

class FakeEmptyHelpResponder(Responder):
    def name(self):
        return 'fake'

    def generate(self, message):
        return "salut"

class TestHelpResponder(BaseTestCase):
    def setUp(self):
        self.responder = HelpResponder()

    def test_support(self):
        self.assertTrue(self.responder.support("help"))
        self.assertFalse(self.responder.support("fuu"))

    def test_on_start(self):
        self.responder.on_start(FakeConsumer([FakeResponder(), FakeEmptyHelpResponder()]))
        self.assertEquals([('fake', '> \n> My help message\n> Look greats from here\n>')], self.responder.helps)

    def test_generate(self):
        self.responder.on_start(FakeConsumer([FakeResponder()]))
        self.assertEquals("# Help\n##fake \n> \n> My help message\n> Look greats from here\n>\n---\n", self.generate("help"))
