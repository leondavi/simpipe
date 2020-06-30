
from Definitions import *
import os
import Instruction
import csv

class Memory:
    def __init__(self,mem_params:dict,tables_prefix = DEAFULT_TABLE_PREFIX):
        self.main_memory = []
        self.header = []
        self.load_memory(mem_params,tables_prefix)
        self.instruction_keys = self.set_instruction_keys(self.header)


    def load_memory(self,mem_params:dict,tables_prefix):
        mem_path = mem_params['mem_path']
        max_ptr = mem_params['ptrMax']
        if mem_path.endswith("csv"):
            csv_files = [mem_path]
        else:  # multiple CSV
            files = os.listdir(mem_path)
            csv_files = [(int(file.split(".")[0].split("_")[-1]), file)
                         for file in files if file.endswith("csv") and file.startswith(tables_prefix)]
            csv_files.sort()
            csv_files = [os.path.join(mem_path, file[1]) for file in csv_files]

        self.memory = []
        for csv_table_path in csv_files:
            with open(csv_table_path) as f:
                reader = csv.reader(f)
                new_memory_sector = list(reader)
                if self.is_header(new_memory_sector[0]):
                    self.header = new_memory_sector[0]
                    del new_memory_sector[0]
                new_memory_sector = self.fix_reversed_memory(new_memory_sector)
                self.main_memory += new_memory_sector
            f.close()

            # Check if max size is set, and if the total read exceed that size.
            if max_ptr and len(self.main_memory) >= max_ptr:
                self.main_memory = self.main_memory[0:max_ptr]
                return

    @staticmethod
    def set_instruction_keys(headers_list : list):
        return {val: idx for idx, val in enumerate(headers_list)}

    def len(self):
        return len(self.main_memory)

    def get_row(self,row_idx : int) -> list:
        if row_idx < len(self.main_memory):
            return self.main_memory[row_idx]
        return []

    def get_instruction_keys(self):
        return self.instruction_keys

    @staticmethod
    def is_header(mem_list_row: list):
        if not mem_list_row[0].isnumeric():
            return True

    @staticmethod
    def fix_reversed_memory(memory_sector: list):
        if int(memory_sector[0][0]) > int(memory_sector[-1][0]):
            memory_sector = memory_sector[::-1]
        return memory_sector