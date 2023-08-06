# vim: set fileencoding=utf-8 :

class Responder(object):
    def support(message):
        pass

    def generate(message):
        pass
        
    def on_start(self, consumer):
        return False

    def support(self, message):
        return message[0:len(self.name())] == self.name()


class Response(object):
    def __init__(self, content):
        self.content = content
        self.tags = []
        self.command = ""
        
    def __str__(self):
        return self.content

class StreamResponse(Response):
    def __init__(self, content):
        self.is_completed = False
        self.content = content

    def stop(self):
        self.is_completed = True

    def handle(self, request, consumer):
        self.is_completed = True
        

from rageface import RagefaceResponder
from flowdock import FlowdockWhoisResponder
from math import MathResponder
from wat import WatResponder
from xkcd import XkcdResponder
from bigbro import BigbroResponder
from ascii import AsciiResponder
from ninegag import NineGagResponder
from link import LinkResponder
from reminder import ReminderResponder
from status import StatusResponder
from help import HelpResponder
from remote import RemoteResponder
from monitor import MonitorResponder