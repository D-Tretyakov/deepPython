import validators
import socket
import json
import sys

class Client():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        if self.socket is None:
            try:
                self.socket = socket.socket()
            except OSError as e:
                print(f'Error creating socket: {e}')
                exit(1)

            try:
                self.socket.connect((self.host, self.port))
            except OSError as e:
                print(f'Error connecting to {self.host}:{self.port}: {e}')
                exit(1)

    def send(self, data):
        self.connect()

        self.validate(data)

        try:
            self.socket.sendall(data.encode('utf-8'))
        except OSError as e:
            print(f'Error sending data', e)
            self.socket.close()
            exit(1)

        self.socket.settimeout(10)

    def read(self):
        if self.socket is None:
            raise RuntimeError('There is no connection to read from')

        try:
            data = self.socket.recv(1024)
        except socket.timeout as e:
            print('Connection closed by timeout')
        except OSError as e:
            print(f'Error reading from server: {e}')       
        else:
            return json.loads(data.decode('utf-8'))

    def shoutdown(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def validate(self, url):
        if not validators.url(url):
            raise RuntimeError('Invalid URL')
        if sys.getsizeof(url.encode('utf-8')) > 1024:
            raise RuntimeError('Too long input')
