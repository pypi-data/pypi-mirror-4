# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase
import re

class LinkResponder(Responder):
    def __init__(self, links):
        self.links = links

        super(LinkResponder, self).__init__()

    def name(self):
        return "link"

    def support(self, request):
        return True

    def generate(self, request):
        matches = []

        for ereg, sentence in self.links:
            for result in re.finditer(ereg, request.content):
                message = sentence

                for key in result.groupdict():
                    message = message.replace(key, result.groupdict()[key])

                if len(message) > 0:
                    matches.append(message) 

        if len(matches) > 0:
            return " > " + "\n > ".join(matches)

        return False

class TestLinkResponder(BaseTestCase):
    def setUp(self):
        self.responder = LinkResponder([
            ('( |#|^)NONO-(?P<NUMBER>[0-9]*)', 'http://bug/NONO-NUMBER'),
            ('(^| |#)(?P<PROJECT>BUG)-(?P<NUMBER>[0-9]*)', 'http://bug.mycompany.com/browse/PROJECT-NUMBER'),
        ])

    def test_support(self):
        self.assertTrue(self.responder.support("pt"))
        self.assertTrue(self.responder.support("fuu"))

    def test_valid(self):
        self.assertEquals(' > http://bug/NONO-123\n > http://bug/NONO-124', self.generate("Voir le bug NONO-123 et NONO-124"))
        self.assertEquals(' > http://bug/NONO-123', self.generate("Voir le bug NONO-123"))
        self.assertEquals(' > http://bug.mycompany.com/browse/BUG-123', self.generate("BUG-123"))

    def test_on_start(self):
        self.assertFalse(self.responder.on_start(False))
