from fetch_client import Client
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Socket Error Examples')
    parser.add_argument('--host', action="store", dest="host", required=False, default='127.0.0.1')
    parser.add_argument('--port', action="store", dest="port", type=int, required=False, default=1707)
    given_args = parser.parse_args()
    host = given_args.host
    port = given_args.port

    c = Client(host, port)
    c.connect()

    while True:
        try:
            url = input('> ')
            if url != '':
                try:
                    c.send(url)
                except RuntimeError as e:
                    print(e)
                    print('Enter url again')
                    continue
                try:
                    response = c.read()
                except ValueError as e:
                    print('Error decoding JSON')
                    print(e)
                else:
                    print(response)
        except KeyboardInterrupt:
            c.shoutdown()
            print('Session closed')
            break
