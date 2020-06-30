import os
import csv
from Instruction import *
from Pipeline import Pipeline
from Definitions import *


# This class creates and run the Pipeline model
# Receive two parameters dictionary memory and pipeline
#  - mem_params - response on loading the memory
#  - pipeline_params - behavior of the pipeline
class RunModel:

    def __init__(self, mem_params: dict, pipeline_params=dict()):
        self.memory = None
        self.load_mem(mem_params)
        self.pipeline = Pipeline(self.memory, pipeline_params)

    @staticmethod
    def is_header(mem_list_row: list):
        if not mem_list_row[0].isnumeric():
            return True

    @staticmethod
    def fix_reversed_memory(memory_sector: list):
        if int(memory_sector[0][0]) > int(memory_sector[-1][0]):
            memory_sector = memory_sector[::-1]
        return memory_sector

    def load_mem(self, mem_params: dict, table_prefix=DEAFULT_TABLE_PREFIX):

        mem_path = mem_params['mem_path']
        max_ptr = mem_params['ptrMax']
        if mem_path.endswith("csv"):
            csv_files = [mem_path]
        else:  # multiple CSV
            files = os.listdir(mem_path)
            csv_files = [(int(file.split(".")[0].split("_")[-1]), file)
                         for file in files if file.endswith("csv") and file.startswith(table_prefix)]
            csv_files.sort()
            csv_files = [os.path.join(mem_path, file[1]) for file in csv_files]

        self.memory = []
        for csv_table_path in csv_files:
            with open(csv_table_path) as f:
                reader = csv.reader(f)
                new_memory_sector = list(reader)
                if self.is_header(new_memory_sector[0]):
                    Instruction.csv_keys = {val: idx for idx, val in enumerate(new_memory_sector[0])}
                    del new_memory_sector[0]
                new_memory_sector = self.fix_reversed_memory(new_memory_sector)
                self.memory += new_memory_sector
            f.close()

            # Check if max size is set, and if the total read exceed that size.
            if max_ptr and len(self.memory) >= max_ptr:
                self.memory = self.memory[0:max_ptr]
                return

    def simulator(self):
        cur_tick = 0
        while self.pipeline.tick(cur_tick):
            cur_tick += 1

    def report_statistics(self):
        self.pipeline.report_statistics()
