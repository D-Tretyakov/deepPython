import signal
import os
import time

def receive_signal(signalNumber, frame):
    print('Received:', signalNumber)
    raise SystemExit('Exiting')
    return

if __name__ == '__main__':
    signal.signal(signal.SIGUSR1, receive_signal)
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    print('My PID is:', os.getpid())
    signal.pause()