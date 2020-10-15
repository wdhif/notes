#!/usr/bin/env python3

import concurrent.futures
import os
import random
import threading
import time

def wait(seconds):
    print(f'Waiting {round(seconds, 2)}s. PID: {os.getpid()}')
    time.sleep(seconds)
    return f'Done sleeping for {round(seconds, 2)}s'


if __name__ == '__main__':
    start = time.perf_counter()

    print('Basic Example')  # Basic Example
    thread_1 = threading.Thread(target=wait, args=[random.random()])
    thread_2 = threading.Thread(target=wait, args=[random.random()])

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()

    print('For-loop Example')  # For-loop Example
    thread_list = []
    for _ in range(3):
        thread = threading.Thread(target=wait, args=[random.random()])
        thread.start()
        thread_list.append(thread)

    for thread in thread_list:
        thread.join()

    print(f'concurrent.futures.ThreadPoolExecutor Example')  # concurrent.futures Example
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(wait, random.random()) for _ in range(3)]  # Returns a future object
        for future in futures:
            print(future.result())

        results = executor.map(wait, [random.random() for _ in range(3)])  # Returns an iterator with result as string
        for result in results:
            print(result)

    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2)}s')

