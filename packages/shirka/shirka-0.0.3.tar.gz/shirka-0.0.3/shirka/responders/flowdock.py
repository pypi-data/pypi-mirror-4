# vim: set fileencoding=utf-8 :

from shirka.responders import Responder
from shirka.consumers import BaseTestCase
import requests

class FlowdockWhoisResponder(Responder):
    def __init__(self, organisation, flow, token):
        """consumer(flowdock)

        flowdock - The flowdock instance
        """
        self.organisation = organisation
        self.flow = flow
        self.token = token

    def name(self):
        return 'whois'

    def generate(self, request):
        """
        usage: whois user
        retrieves user information from Flowdock API
        """
        words = request.content.split(" ")

        user = False
        if not words[1].isdigit():
            users = requests.get("https://api.flowdock.com/flows/%s/%s/users" % (self.organisation, self.flow), auth=(self.token, '')).json()

            for u in users:
                if u['nick'] == words[1]:
                    user = u
                    break
        else:
            user = requests.get("https://api.flowdock.com/users/%s" % words[1], auth=(self.token, '')).json()    

        if user:
            return {
                'content': "%s is %s - %s (id:%s)" % (words[1], user['name'], user['email'], user['id']),
                'tags': ['#contact']
            }

        return False
        

class TestFlowdockWhoisResponder(BaseTestCase):
    def setUp(self):
        self.responder = FlowdockWhoisResponder('orga', 'flow', 'token')

    def test_support(self):
        self.assertTrue(self.responder.support("whois"))
        self.assertFalse(self.responder.support("fuu"))

    def test_on_start(self):
        self.assertFalse(self.responder.on_start(False))

