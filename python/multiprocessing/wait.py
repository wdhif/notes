#!/usr/bin/env python3

import concurrent.futures
import multiprocessing
import os
import random
import time

def wait(seconds):
    print(f'Waiting {round(seconds, 2)}s. PID: {os.getpid()}')
    time.sleep(seconds)
    return f'Done sleeping for {round(seconds, 2)}s'


if __name__ == '__main__':
    start = time.perf_counter()

    print('Basic Example')  # Basic Example
    process_1 = multiprocessing.Process(target=wait, args=[random.random()])
    process_2 = multiprocessing.Process(target=wait, args=[random.random()])

    process_1.start()
    process_2.start()

    process_1.join()
    process_2.join()

    print('For-loop Example')  # For-loop Example
    process_list = []
    for _ in range(3):
        process = multiprocessing.Process(target=wait, args=[random.random()])
        process.start()
        process_list.append(process)

    for process in process_list:
        process.join()

    print(f'concurrent.futures.ProcessPoolExecutor Example')  # concurrent.futures Example
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(wait, random.random()) for _ in range(3)]  # Returns a future object
        for future in futures:
            print(future.result())

        results = executor.map(wait, [random.random() for _ in range(3)])  # Returns an iterator with result as string
        for result in results:
            print(result)

    finish = time.perf_counter()
    print(f'Finished in {round(finish-start, 2)}s')
