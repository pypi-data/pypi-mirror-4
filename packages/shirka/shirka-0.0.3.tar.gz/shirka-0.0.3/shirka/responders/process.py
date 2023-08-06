# vim: set fileencoding=utf-8 :
from shirka.responders import Responder, StreamResponse
from shirka.consumers import BaseTestCase
from shirka.tools import process
import paramiko, functools

class ProcessStreamResponse(StreamResponse):
    def __init__(self, proc, server, bot):
        self.server = server
        self.proc = proc
        self.bot = bot

    def handle(self, request, consumer):
        consumer.post("Starting process: %s@%s$ %s -\n%s#/process/%s" % (self.proc.user, self.proc.server, self.proc.command, self.bot.url, self.proc.id), request)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            host = self.server['host']
            args = self.server
            del(args['host'])

            client.connect(host, **args)
        except paramiko.BadHostKeyException, e:
            consumer.post("BadHostKeyException: %s" % self.name, request)

        except paramiko.AuthenticationException, e:
            consumer.post("AuthenticationException: %s" % self.name, request)

        except paramiko.SSHException, e:
            consumer.post("SSHException: %s" % self.name, request)

        try:
            self.bot.process_executor.run(self.proc, functools.partial(process.paramiko_run, client))

            consumer.post("[OK] Process is completed: %s@%s$ %s -\n%s#/process/%s" % (self.proc.user, self.proc.server, self.proc.command, self.bot.url, self.proc.id), request)

        except paramiko.SSHException, e:
            consumer.post("[KO] An error occurs while executing the process: %s@%s$ %s -\n%s#/process/%s" % (self.proc.user, self.proc.server, self.proc.command, self.bot.url, self.proc.id), request)

        finally:
            client.close()


class ProcessResponder(Responder):
    def __init__(self, servers, users, commands, bot):
        self.servers = servers
        self.users = users
        self.commands = commands
        self.bot = bot

    def name(self):
        return "process"

    def generate(self, request):
        """
        usage: process server registered_command
        run a command on an remote server
        """
        if request.user.id not in self.users:
            return "You fool, you are not my master!!"

        words = request.content.split(" ", 2)

        if len(words) < 2:
            return "Invalid command"

        if words[1] not in self.servers:
            return "Sorry, there is no such server available"

        if words[2] not in self.commands:
            return "Sorry, the command keyword does not exist"

        proc = process.Process(self.commands[words[2]])
        proc.server = words[1]
        proc.user = request.user.id

        return ProcessStreamResponse(proc, self.servers[words[1]].copy(), self.bot)

class TestProcessResponder(BaseTestCase):
    def setUp(self):
        self.responder = ProcessResponder(
            { 'nono': {} },
            [1],
            { 'ls' : 'ls -ls'},
            None
        )

    def test_support(self):

        from shirka.consumers import Request, User

        request = Request("process nono ls", User('name', 'email@email.com', 1), "type", "test provider")
        response = self.responder.generate(request)

        self.assertIsInstance(response, ProcessStreamResponse)



