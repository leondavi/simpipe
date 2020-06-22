
import csv
from Pipeline import Pipeline


SIMULATION_FILE = "../data/dummy.csv"
NUM_OF_THREADS = 1
PIPELINE_STAGES = 5

Memory = None
with open(SIMULATION_FILE) as f:
    reader = csv.reader(f)
    Memory = list(reader)


def simulator():
    pipeline = Pipeline(NUM_OF_THREADS)



simulator()






