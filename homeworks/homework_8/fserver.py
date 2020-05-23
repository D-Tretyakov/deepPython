import nltk; from nltk.corpus import stopwords
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from collections import Counter
from bs4 import BeautifulSoup
from queue import Queue
import threading as th
import validators
import signal
import socket
import json
import sys
import re
import os

import logging
FORMAT_STR = '%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s'
LOG_FILE = "server.log"
logging.basicConfig(format=FORMAT_STR, filename=LOG_FILE, level=logging.INFO)

WORKERS = 4
MOST_FREQ = 10
ENG_STOP_WORDS = stopwords.words('english')
RU_STOP_WORDS = stopwords.words('russian')

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.q = Queue(100)
        self.sentinel = object()
        self.threads = [th.Thread(target=self.download, args=(i+1,)) for i in range(WORKERS)]
        self.lock = th.Lock()
        self.message = []
        self.downloaded = 0
        self.signal_shutdown = False

        for thread in self.threads:
            thread.start()

        signal.signal(signal.SIGUSR1, self.signal_handler)

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
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            except OSError as e:
                print(f'Error creating socket: {e}')
                exit(1)
            
            try:
                self.socket.bind((self.host, self.port))
            except OSError as e:
                print(f'Error binding socket: {e}')
                exit(1)                
            
            self.socket.listen(5)
            while True:

                try:
                    client, address = self.socket.accept()
                except OSError as e:
                    print(f'Error accepting connection: {e}')

                th.Thread(target=self.listen_to_client, args=(client, address)).start()
        else:
            raise RuntimeError('Server is already running')

    def stop(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        else:
            raise RuntimeError('Server isn\'t running')

        self.lock.acquire()
        while not self.q.empty():
            self.q.get()

        for _ in range(WORKERS):
            self.q.put((self.sentinel, None))
        self.lock.release()
        
        if self.threads:
            for thread in th.enumerate():
                if thread is not th.main_thread():
                    thread.join()
    
    def listen_to_client(self, connection, address):
        print('Connected:', address)
        with connection:
            client_q = Queue(10)
            while True:
                if self.signal_shutdown:
                    self.send({'url': None, 'body': '<SHUTDOWN>'}, connection)
                    break

                try:
                    data = connection.recv(1024)
                except OSError as e:
                    print(f'Error reading from client: {e}')
                else:
                    if not data:
                        break

                    url = data.decode('utf-8').strip()
                    print(url)
                    if self.is_valid(url):
                        self.q.put((url, client_q))
                    else:
                        self.send({'url': None, 'body': 'There\'s invalid url'}, connection)
                        break
                    
                    txt = client_q.get()
                    self.send(txt, connection)
                    while not client_q.empty():
                        txt = client_q.get()
                        self.send(txt, connection)


    def send(self, raw_text, connection):
        text = json.dumps(raw_text)
        size = sys.getsizeof(f'<text>{text}<text>'.encode('utf-8'))
        connection.sendall(f'<size>{size}<size>'.encode('utf-8'))
        answer = connection.recv(1024).decode('utf-8')
        if answer == '<OK>':
            connection.sendall(f'<text>{text}<text>'.encode('utf-8'))

    def parse(self, response, url):
        if response is None:
            return {'url': url, 'body': 'Something went wrong'}
        else:
            html = response.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        for script_tag in soup(["script", "style"]):
            script_tag.decompose()

        words = [word.lower().strip() for word in re.sub(r'[^a-zA-Zа-яА-Я]', ' ', soup.get_text()).split() if len(word.strip()) > 1]

        freq_dict = Counter(filter(lambda x: len(x) > 1 and x not in ENG_STOP_WORDS and x not in RU_STOP_WORDS, words))
        return {'url': response.url, 'body': dict(freq_dict.most_common(MOST_FREQ))}


    def download(self, thread_num):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        while True:
            url, client_q = self.q.get()
            print(f'Thread-{thread_num}: got {url}')
            if url is self.sentinel:
                break

            query = Request(url, headers=headers)
            response = None
            try:
                response = urlopen(query, timeout=10)
            except HTTPError as e:
                print('The server couldn\'t fulfill the request')
                print('Error code:', e.code)
                logging.error(f'({url}) HTTP Error: {e.code}')
            except URLError as e:
                print('Failed to reach a server')
                print('Reason:', e.reason)
                logging.error(f'({url}) Failed to reach a server: {e.reason}')
            except socket.timeout:
                print('Connection timeout')
                logging.error(f'({url}) connection timeout')


            page_text = self.parse(response, url)

            client_q.put(page_text)
            self.lock.acquire()
            self.downloaded += 1
            print(f'Thread-{thread_num}: sended')
            self.lock.release()
        print(f'Thread-{thread_num}: ended')
    
    def signal_handler(self, signalNumber, frame):
        print('Received signal to stop')
        self.signal_shutdown = True
        exit(0)

    def is_valid(self, url):
        if not validators.url(url):
            return 0
        return 1
