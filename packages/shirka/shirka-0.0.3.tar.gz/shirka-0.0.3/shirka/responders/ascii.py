# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase
import requests, re

class AsciiResponder(Responder):
    def name(self):
        return 'ascii'

    def generate(self, request):
        """
        usage: ascii message
        Generate an ascii art from the provided message
        """
        payload = {'s': request[6:]}
        ascii = requests.get('http://asciime.heroku.com/generate_ascii', params=payload).text
        
        return re.sub('^|\n', '\n\t', ascii)

class TestAsciiResponder(BaseTestCase):
    def setUp(self):
        self.responder = AsciiResponder()

    def test_support(self):
        self.assertTrue(self.responder.support("ascii"))
        self.assertFalse(self.responder.support("fuu"))

    def test_valid(self):
        self.assertIsNotNone(self.generate("ascii wat"))

    def test_on_start(self):
        self.assertFalse(self.responder.on_start(False))
