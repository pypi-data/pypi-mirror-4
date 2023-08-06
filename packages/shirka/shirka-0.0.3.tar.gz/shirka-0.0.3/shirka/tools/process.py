from threading import Thread
import uuid, datetime, os, json

class BuffersReader(object):
    def __init__(self, path):
        self.path = path

    def store(self, path, stdout, stderr=None):
        def rw(path, stream):
            f = file(path, 'w')

            while True:
                line = stream.readline()

                if line == '':
                    break

                f.write(line)

            f.close()

        if stderr:
            self.terr = Thread(target=rw, args=("%s/stderr" % (self.path), stderr))
            self.terr.start()

        rw("%s/stdout" % (self.path), stdout)


def paramiko_run(client, process):
    stdin, stdout, stderr = client.exec_command(process.command)

    return (stdin, stdout, stderr)

class ProcessExecutor(object):
    def __init__(self, path):
        self.path = path

    def save_state(self, process):
        path = self.get_path(process)
        if not os.path.isdir(path):
            os.makedirs(path)

        f = file('%s/state.json' % path, 'w')
        f.write(json.dumps(process.info()))
        f.close()

    def get_path(self, process):
        return "%s/%s" % (self.path, process.id)

    def get_process(self, id):
        data = json.loads(file("%s/%s/state.json" % (self.path, process.id)).read())

        return Process.create(data)

    def run(self, process, callback):
        self.save_state(process)

        process.started_at = datetime.datetime.today()
        process.state = 'started'
        self.save_state(process)

        stdin, stdout, stderr = callback(process)

        buffer_reader = BuffersReader(self.get_path(process))
        buffer_reader.store(process.id, stdout, stderr=stderr)

        process.finished_at = datetime.datetime.today()
        process.state = 'completed'

        self.save_state(process)

class Process(object):
    def __init__(self, command):
        self.command = command
        self.id = str(uuid.uuid4())
        self.state = 'init'
        self.created_at = datetime.datetime.today()
        self.started_at = datetime.datetime.today()
        self.finished_at = datetime.datetime.today()
        self.server = ''
        self.user = ''

    def info(self):
        return {
            'command': self.command,
            'id': self.id,
            'state': self.state,
            'created_at': str(self.created_at),
            'started_at': str(self.started_at),
            'finished_at': str(self.finished_at),
            'server': self.server,
            'user': self.user
        }

    def create(data):
        process = Process(data['command'])
        process.id = data['id']
        process.state = data['state']
        process.created_at = data['created_at']
        process.started_at = data['started_at']
        process.finished_at = data['finished_at']
        process.server = data['server']
        process.user = data['user']

        return process