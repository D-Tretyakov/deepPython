import socket
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

TIMEOUT = 10
# socket.setdefaulttimeout(TIMEOUT)

class HttpRequest():
    def __init__(self, url, headers=None):
        if headers is None:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}

        query = Request(url, headers=headers)
        self.response = None
        try:
            self.response = urlopen(query, timeout=10)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request')
            print('Error code:', e.code)
        except URLError as e:
            print('Failed to reach a server')
            print('Reason:', e.reason)

    def read(self):
        return self.response and self.response.read()

class HttpResponse():
    def __init__(self, body, body_type='application/json'):
        if body_type != 'application/json':
            raise NotImplementedError('Only JSON supported')

        self.body = body
        self.body_type = body_type