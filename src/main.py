
import csv
from Instruction import *
from Pipeline import Pipeline
from Definitions import *


class MainRun:

    def __init(self):
        self.memory = None
        pass

    def simulator(self, memory_file=SIMULATION_FILE, remove_headers=True):
        with open(memory_file) as f:
            reader = csv.reader(f)
            self.memory = list(reader)
        if remove_headers:
            Instruction.csv_keys = {val: idx for idx, val in enumerate(self.memory[0])}
            del self.memory[0]  # Remove headers

        pipeline = Pipeline(self.memory[::-1], NUM_THREADS, NUM_STAGES)
        print(pipeline.headers_str())

        cur_tick = 0
        while pipeline.tick(cur_tick):
            cur_tick += 1

        pipeline.report_statistics()



x = MainRun()
x.simulator()


