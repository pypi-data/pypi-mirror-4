# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase

DEFAULT_IMG = {
    "badumtss": "http://fuuu.us/363.png",
    "cerealguy": "http://fuuu.us/144.png",
    "cute": "http://fuuu.us/447.png",
    "deskflip": "http://fuuu.us/217.png",
    "fuckyeah": "http://fuuu.us/12.png",
    "genius": "http://fuuu.us/292.png",
    "itssomething": "http://fuuu.us/408.png",
    "lol": "http://fuuu.us/176.png",
    "longneck": "http://fuuu.us/107.png",
    "megusta": "http://fuuu.us/35.png",
    "notbad": "http://fuuu.us/172.png",
    "nothing": "http://fuuu.us/230.png",
    "pokerface": "http://fuuu.us/268.png",
    "rageguy": "http://fuuu.us/61.png",
    "sir": "http://fuuu.us/389.png",
    "troll": "http://fuuu.us/86.png",
    "true": "http://fuuu.us/285.png",
    "win": "http://fuuu.us/188.png",
}

class RagefaceResponder(Responder):
    def __init__(self, faces=DEFAULT_IMG):
        self.faces = faces

    def name(self):
        return 'face'

    def generate(self, request):
        """
        usage: rageface [face] : display the related rageface
               rageface help : display faces available
        """
        words = request.content.split(" ")

        if len(words) < 2:
            return False

        if words[1] == 'help':
            return "Face available: %s" % (", ".join(self.faces))

        if words[1] in self.faces:
            return self.faces[words[1]]

        return "You fail!! This face does not exist"


class TestRagefaceResponder(BaseTestCase):
    def setUp(self):
        self.responder = RagefaceResponder()

    def test_support(self):
        self.assertTrue(self.responder.support("face"))
        self.assertFalse(self.responder.support("fuu"))

    def test_incomplete_command(self):
        self.assertFalse(self.generate("face"))

    def test_help(self):
        self.assertIsNotNone(self.generate("face help"))

    def test_valid(self):
        self.assertEquals(self.generate("face win"), "http://fuuu.us/188.png")

    def test_on_start(self):
        self.assertFalse(self.responder.on_start(False))

        