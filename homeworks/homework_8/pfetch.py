from queue import Queue
import threading as th
import argparse
import socket
import json

from fclient import Client

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action="store", dest="host", required=False, default='127.0.0.1')
    parser.add_argument('--port', action="store", dest="port", type=int, required=False, default=1707)
    parser.add_argument('--file', action="store", dest="file", type=str, required=True)
    parser.add_argument('-m', action="store", dest="m", type=int, required=False, default=4)
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port
    file = given_args.file
    m = given_args.m

    c = Client(host, port, m)
    c.add_to_queue(file)
    c.run()