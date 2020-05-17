from fetch_server import Server
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket Error Examples')
    parser.add_argument('--host', action="store", dest="host", required=False, default='127.0.0.1')
    parser.add_argument('--port', action="store", dest="port", type=int, required=False, default=1707)
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port

    with Server(host, port) as s:
        s.run()
        print(f'Server running on {host}:{port}')
        while True:
            try:
                s.make_connection()
            except KeyboardInterrupt:
                print('Shoutdown')
                break