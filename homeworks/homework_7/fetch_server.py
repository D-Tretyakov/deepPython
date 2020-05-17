from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from request_response import HttpRequest, HttpResponse
import nltk; from nltk.corpus import stopwords
from collections import Counter
from bs4 import BeautifulSoup
import urllib.request
import validators
import socket
import json
import re

STOP_WORDS = stopwords.words('english')

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        if exc_val:
            raise

    def run(self):
        if self.socket is None:
            try:
                self.socket = socket.socket()
            except OSError as e:
                print(f'Error creating socket: {e}')
                exit(1)
            
            try:
                self.socket.bind((self.host, self.port))
            except OSError as e:
                print(f'Error binding socket: {e}')
                exit(1)                
            
            self.socket.listen()
        else:
            raise RuntimeError('Server is already running')

    def stop(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        else:
            raise RuntimeError('Server isn\'t running')

    def make_connection(self):
        try:
            connection, address = self.socket.accept()
        except OSError as e:
            print(f'Error accepting connection: {e}')

        with connection:
            print('Connected: ', address)

            recieved = list()
            while True:
                try:
                    data = connection.recv(1024)
                except OSError as e:
                    print(f'Error reading from client: {e}')
                else:
                    if not data:
                        break

                    url = data.decode('utf-8')
                    print(url)
                    if not self.is_valid(url):
                        connection.sendall('Invalid url'.encode('utf-8'))
                    else:
                        request = HttpRequest(url)
                        response = self.parse_query(request)
                        connection.sendall(response.body.encode('utf-8'))

    def parse_query(self, request):
        html = request.read()
        if html is None:
            return HttpResponse(body='Something went wrong')
        
        soup = BeautifulSoup(html, 'html.parser')
        for script_tag in soup.find_all('script'):
            script_tag.decompose()

        words = [re.sub(r'[^a-zA-Zа-яА-Я]', ' ', word.lower()).strip() for word in soup.get_text().split()]

        freq_dict = Counter(filter(lambda x: len(x) > 1 and x not in STOP_WORDS, words))
        response_body = json.dumps(dict(freq_dict.most_common(10)))

        return HttpResponse(body=response_body)

    def is_valid(self, url):
        if not validators.url(url):
            return 0
        return 1
