
import csv
from Pipeline import Pipeline


SIMULATION_FILE = "../data/dummy.csv"
NUM_OF_THREADS = 1
PIPELINE_STAGES = 5


def simulator(memory_file = SIMULATION_FILE,removeHeaders = True):

    Memory = None
    with open(memory_file) as f:
        reader = csv.reader(f)
        Memory = list(reader)
    if removeHeaders:
        del Memory[0] #remove headers

    pipeline = Pipeline(NUM_OF_THREADS,PIPELINE_STAGES,Memory)
    print (pipeline.headers_str())




simulator()






