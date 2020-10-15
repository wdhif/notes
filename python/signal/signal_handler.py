#!/usr/bin/env python3

import os
import signal
import time

def sigusr1_handler(signum, frame):
    print(f'Catched a SIGUSR1 signal: {signum}, {frame}')

def sigusr2_handler(signum, frame):
    print(f'Catched a SIGUSR2 signal: {signum}, {frame}')

def main():
    print(f'PID: {os.getpid()}')
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    signal.signal(signal.SIGUSR2, sigusr2_handler)
    print('Waiting 300s to catch signals')
    time.sleep(300)


if __name__ == '__main__':
    main()
