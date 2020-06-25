
import csv
from Pipeline import Pipeline
from Definitions import *


def simulator(memory_file=SIMULATION_FILE, remove_headers=True):
    with open(memory_file) as f:
        reader = csv.reader(f)
        memory = list(reader)
    if remove_headers:
        del memory[0]  # Remove headers

    pipeline = Pipeline(memory, NUM_THREADS, NUM_STAGES)
    print(pipeline.headers_str())

    cur_tick = 0
    while pipeline.tick(cur_tick):
        cur_tick += 1


simulator()
