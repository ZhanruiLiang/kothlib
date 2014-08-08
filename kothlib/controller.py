import os
import subprocess
import logging
import shlex
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed


log = logging.warning


class Controller:
    def __init__(self):
        self.__clients = []

    def collect(self, path, command_name, exclude=()):
        self.__clients = []
        for dir in os.listdir(path):
            if dir in exclude:
                continue
            self.__clients.append(Client(
                dir,
                os.path.join(path, dir),
                os.path.join(path, dir, command_name)
            ))

    def sort(self, key=lambda client: client.name):
        self.__clients.sort(key=key)

    def kill_all(self):
        for client in self.iter_alive():
            client.kill()

    def send_all(self, data):
        for client in self.iter_alive():
            client.send(data)

    def receive_all(self, timeout=None):
        future_to_client = {}
        with ThreadPoolExecutor(max_workers=len(self.__clients)) as executor:
            for client in self.iter_alive():
                client.result = None
                future = executor.submit(client._proc.stdout.readline)
                future_to_client[future] = client
            try:
                for future in as_completed(future_to_client.keys(), timeout=timeout):
                    client = future_to_client[future]
                    client.result = future.result()[:-1].decode()
            except TimeoutError:
                for future, client in future_to_client.items():
                    if not future.done():
                        log('client({}) timeout({}) during receive, canceling'.format(client.name, timeout))
                        client.kill()
                        future.cancel()

    def __iter__(self):
        return iter(self.__clients)

    def iter_alive(self):
        for client in self.__clients:
            if client.alive:
                yield client


class Client:
    def __init__(self, name, work_dir, command_path):
        self.name = name
        self.result = None
        command = shlex.split(open(command_path).read())
        self._proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=work_dir
        )

    @property
    def alive(self):
        return self._proc.returncode is None

    def __hash__(self):
        return hash(self.name)

    def send(self, data):
        try:
            self._proc.stdin.write((data + '\n').encode())
            self._proc.stdin.flush()
        except BrokenPipeError as error:
            log('fail to send to client({}): {}'.format(self.name, error))
            self.kill()

    def receive(self, timeout=None):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._proc.stdout.readline)
            try:
                result = future.result(timeout)[:-1].decode()
            except TimeoutError:
                log('client({}) timeout({}) during receive, canceling'.format(self.name, timeout))
                future.cancel()
                result = None
            return result

    def kill(self):
        log('kill client, name={}'.format(self.name))
        self._proc.kill()
        self._proc.poll()
