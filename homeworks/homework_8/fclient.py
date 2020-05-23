from queue import Queue
import threading as th
import argparse
import socket
import json

class Client():
    def __init__(self, host, port, m, qsize=100):
        self.host = host
        self.port = port
        self.m = m
        self.downloaded = 0
        self.q = Queue(qsize)
        self.threads = None
        self.signal_shutdown = False
        self.lock = th.Lock()

    def add_to_queue(self, file):
        with open(file) as f:
            for i in f.readlines():
                self.q.put(i)
    
    def get_response(self, sock):
        raw_size = sock.recv(1024).decode('utf-8')
        if raw_size.startswith('<size>') and raw_size.endswith('<size>'):
            size = int(raw_size[6:-6])
        
        sock.sendall('<OK>'.encode('utf-8'))
        
        raw_text = sock.recv(size).decode('utf-8')
        if raw_text.startswith('<text>') and raw_text.endswith('<text>'):
            text = raw_text[6:-6]
            if text == '<SHUTDOWN>':
                self.signal_shutdown = True
                return
        
        return json.loads(text)
    
    def ask_server(self):
        try:
            s = socket.socket()
            s.connect((self.host, self.port))
        except:
            print('critical error with socket')
            return
        while not self.q.empty():
            if self.signal_shutdown:
                s.close()
                break
            url = self.q.get()

            try:
                s.sendall(url.encode('utf-8'))
                r = self.get_response(s)
            except:
                print('error with socket')
                return

            self.lock.acquire()
            if r['body'] != 'Something went wrong':
                self.downloaded += 1
            self.lock.release()
            print(r)

    def run(self):
        self.threads = [th.Thread(target=self.ask_server) for i in range(self.m)]
        for thread in self.threads:
            thread.start()
    
        for thread in th.enumerate():
            if thread is not th.main_thread():
                thread.join()
        
        print('Downloaded', self.downloaded)