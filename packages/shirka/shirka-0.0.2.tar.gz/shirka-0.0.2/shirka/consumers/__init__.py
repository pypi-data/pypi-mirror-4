# vim: set fileencoding=utf-8 :

import unittest

class Bot(object):
    def __init__(self, name, email):
        self.name = name
        self.email = email

class User(object):
    def __init__(self, name, email, id):
        self.name = name
        self.email = email
        self.id = id

    def __repr__(self):
        return self.name

class Request(object):
    def __init__(self, content, user, type, provider):
        self.content = content
        self.user = user
        self.type = type
        self.provider = provider

    def __str__(self):
        return self.content

    def __unicode__(self):
        return self.content

    def __repr__(self):
        return self.content

    def __getitem__(self, key):
        print self.content
        
        return self.content[key]


class BaseTestCase(unittest.TestCase):
    def create_request(self, message):
        return Request(message, None,  None,  None)

    def generate(self, message):
        return self.responder.generate(self.create_request(message))


class TestRequest(BaseTestCase):
    def setUp(self):
        self.request = self.create_request("the content")

    def test_slice(self):
        self.assertEquals("the", self.request[0:3])

    def test_unicode(self):
        self.request = self.create_request(u"étrange...")
        self.assertEquals(u"étrange...", u"%s" % self.request)
        

from flowdock import FlowDockConsumer