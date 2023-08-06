# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase

import requests
import exceptions

class XkcdResponder(Responder):
    def name(self):
        return "xkcd"
        
    def generate(self, request):
        """
        usage: xkcd integer
        retrieves xkcd image from the provided integer
        """
        try:
            r = requests.get('http://xkcd.com/%s/info.0.json' % request[5:]).json()
        except exceptions.ValueError, e:
            return False

        return r['img']

class TestXkcdResponder(BaseTestCase):
    def setUp(self):
        self.responder = XkcdResponder()

    def test_support(self):
        self.assertTrue(self.responder.support("xkcd"))
        self.assertFalse(self.responder.support("fuu"))

    def test_valid(self):
        self.assertEquals(self.generate("xkcd 1"), "http://imgs.xkcd.com/comics/barrel_cropped_(1).jpg")

    def test_invalid(self):
        self.assertFalse(self.generate("xkcd fake"))

    def test_on_start(self):
        self.assertFalse(self.responder.on_start(False))
