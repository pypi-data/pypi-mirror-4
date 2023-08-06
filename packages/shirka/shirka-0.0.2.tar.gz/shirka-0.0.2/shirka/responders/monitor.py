# vim: set fileencoding=utf-8 :

from shirka.responders import Responder, StreamResponse
from shirka.consumers import BaseTestCase
import requests, time

class StreamMonitorResponse(StreamResponse):
    def __init__(self, servers):
        self.servers = servers
        self.status = {
            'http' : {}
        }
    
    def get_http_args(self, options):

        args = {}
        if 'auth' in options:
            args['auth'] = (options['auth'][0], options['auth'][1])
        
        if 'verify' in options:
            args['verify'] = options['verify']

        if 'timeout' in options:
            args['timeout'] = float(options['timeout'])
        else:
            args['timeout'] = 5

        if 'allow_redirects' not in options:
            args['allow_redirects'] = False

        return args

    def check_response(self, response):
        if response.status_code >= 200 and response.status_code < 400:
            return True

        return False

    def monitor_http(self):
        if 'http' not in self.servers:
            return

        for server_name in self.servers['http']:
            server = self.get_server('http', server_name)

            try:
                http_response = requests.get(server['url'], **self.get_http_args(server['options']))
            except requests.exceptions.RequestException, e:
                self.handle_http_error(server_name)
                continue

            if self.check_response(http_response):
                self.handle_http_ok(server_name)
            else:
                self.handle_http_error(server_name)
                
    def get_server(self, type, server_name):
        return self.servers[type][server_name]

    def get_status(self, type, server_name):
        if server_name not in self.status[type]:
            self.status[type][server_name] = {'status': 'unknown', 'retry': 0, 'error': 0}

        return self.status[type][server_name]

    def handle_http_ok(self, server_name):
        server = self.get_server('http', server_name)
        status = self.get_status('http', server_name)

        if status['status'] == 'ko':
            self.consumer.post("Monitor: [OK] the server %s - %s is now up!" % (server_name, server['url']), self.request)

        status['status'] = 'ok'
        status['retry'] = 0


    def handle_http_error(self, server_name):

        server = self.get_server('http', server_name)
        status = self.get_status('http', server_name)

        status['status'] = 'ko'
        status['retry'] = status['retry'] + 1
        status['error'] = status['error'] + 1

        if status['retry'] == 5:
            self.consumer.post("Monitor: [KO] the server %s - %s fails to response (5 times in a row)" % (server_name, server['url']), self.request)
        elif status['retry'] % 1000 == 0:
            self.consumer.post("Monitor: [KO] the server %s - %s fails to response" % (server_name, server['url']), self.request)


    def handle(self, request, consumer):
        self.request = request
        self.consumer = consumer
        
        while(1):
            self.monitor_http()
            time.sleep(5)


class MonitorResponder(Responder):
    def __init__(self, servers):
        self.servers = servers
        self.monitor = StreamMonitorResponse(self.servers)
    
    def name(self):
        return 'monitor'

    def on_start(self, consumer):
        return self.monitor

    def generate(self, request):
        """
        usage: monitor
        """
        words = request.content.split(" ", 2)

        if len(words) > 1 and words[1] == 'full':
            response = ["# Monitor"]

            response.append("## http")

            for key in self.monitor.status['http']:
                response.append("> %s : %s %s" % (self.monitor.status['http'][key]['status'], key, self.servers['http'][key]['url']))

            return "\n".join(response)
        else:
            for key in self.monitor.status['http']:
                if self.monitor.status['http'][key]['status'] == 'ko':
                    return "Some components are not responding, please run `monitor full` for more information"

            return "All components are running"


class TestMonitorResponder(BaseTestCase):
    def setUp(self):
        self.responder = MonitorResponder({
            'http': {}
        })

    def test_support(self):
        self.assertTrue(self.responder.support("monitor"))
        self.assertFalse(self.responder.support("fuu"))

    def test_valid(self):
        self.assertEquals("All components are running", self.generate("monitor"))

    def test_on_start(self):
        self.assertIsInstance(self.responder.on_start(False), StreamMonitorResponse)
