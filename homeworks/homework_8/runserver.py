from fserver import Server
import argparse
import signal
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action="store", dest="host", required=False, default='127.0.0.1')
    parser.add_argument('--port', action="store", dest="port", type=int, required=False, default=1707)
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port

    with Server(host, port) as s:
        print(f'Server running on {host}:{port}')
        print(f'PID: {os.getpid()}')
        try:
            s.run()
        except KeyboardInterrupt:
            print(' Shutdown')