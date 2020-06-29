
import csv
import os
from idlelib import run
import sys

from Instruction import *
from Pipeline import Pipeline
from Definitions import *
from RegressionPermutation import *

MEM_DICT = {'mem_path':SIMULATION_FILE,'ptrMax':None}

class MainRun:

    def __init__(self,mem_params = dict(),pipeline_params=dict()):
        self.memory = None
        self.load_mem(mem_params)
        self.pipeline = Pipeline(self.memory, pipeline_params)
        pass

    @staticmethod
    def is_header(mem_list_row : list):
        if not mem_list_row[0].isnumeric():
            return True

    @staticmethod
    def fix_revesed_memory(memory_sector : list):
        if int(memory_sector[0][0]) > int(memory_sector[-1][0]):
            memory_sector = memory_sector[::-1]
        return memory_sector

    def load_mem(self, mem_params : dict, table_prefix = DEAFULT_TABLE_PREFIX, remove_headers=True):
        csv_files = list()
        mem_path = mem_params['mem_path']
        max_ptr = mem_params['ptrMax']
        if mem_path.endswith("csv"):
            csv_files = [mem_path]
        else:  # multiple csvs
            files = os.listdir(mem_path)
            csv_files = [(int(file.split(".")[0].split("_")[-1]),file) for file in files if file.endswith("csv") and file.startswith(table_prefix)]
            csv_files.sort()
            csv_files = [os.path.join(mem_path,file[1]) for file in csv_files]

        self.memory = []
        for csv_table_path in csv_files:
            with open(csv_table_path) as f:
                reader = csv.reader(f)
                new_memory_sector = list(reader)
                if self.is_header(new_memory_sector[0]):
                    Instruction.csv_keys = {val: idx for idx, val in enumerate(new_memory_sector[0])}
                    del new_memory_sector[0]
                new_memory_sector = self.fix_revesed_memory(new_memory_sector)
                self.memory += new_memory_sector
            f.close()

    def simulator(self):
        cur_tick = 0
        while self.pipeline.tick(cur_tick):
            cur_tick += 1

        self.pipeline.report_statistics()


def run_rgr():
    mem_params = mem_params_from_args(args_params)
    # generate permutations
    num_thread_list = [1, 2, 4]
    issue_policy_list = ["RR", "COARSE", "EVENT"]
    speculative_list = [False, True]
    num_stages_list = [4]
    prefetch_delay_list = [3]

    rgr = [["NUM_THREAD", num_thread_list], ["ISSUE_POLICY", issue_policy_list],
            ["SPECULATIVE", speculative_list], ["NUM_STAGES", num_stages_list],
            ["PREFETCH_DELAY", prefetch_delay_list]]

    rgr_db = RegressionPermutation(rgr)

    for perm_list in rgr_db.perm_list_of_lists:
        params_dict = dict()
        params_list = list()
        for perm in perm_list:
            key, val = perm.split(":")
            params_dict[key] = val
            params_list.append(val)

        x = MainRun(mem_params,params_dict)
        x.simulator()
        params_list.append("{0:.3f}".format(x.pipeline.ipc))
        # x.pipeline.report_model()
        print(",".join(params_list))
        del x, params_dict, params_list


def run_single():
    mem_params = mem_params_from_args()

    x = MainRun(mem_params)
    x.simulator()
    print(x.pipeline.ipc)


def mem_params_from_args():
    mem_params = MEM_DICT
    if 'dir' in args_params:
        mem_params['mem_path'] = args_params['dir']
    if 'ptrMax' in args_params:
        mem_params['ptrMax'] = args_params['ptrMax']

    return mem_params



def bool_arg_parsing(input_str):
    return True if (input_str == "True" or input_str == "1") else False

def help():
    print("\nSimpipe Help Menu\n-------------------\n")
    print("Version: "+VERSION)
    print("<Option>=<Values>")
    print("Option           Value                Info")
    print("dir               str                 directory of csv tables OR csv file of memory")
    print("single         True/False             Running simple simulation of single run of default parameters")
    print("reg            True/False             Running regression simulation from configuration file of parameters")
    print("verbose        True/False             Pipeline verbosity")


args_params = dict()

if __name__ == '__main__':

    args_params["single"] = False
    args_params["reg"] = False
    args_params["verbose"] = False
    args_params["dir"] = SIMULATION_FILE
    args_params["ptrMax"] = None

    for arg in sys.argv[1:]:
       if arg.startswith("dir="):
           args_params["dir"] = arg.split("=")[1]
       elif arg.startswith("single="):
           args_params["single"] = bool_arg_parsing(arg.split("=")[1])
       elif arg.startswith("reg="):
           args_params["reg"] = bool_arg_parsing(arg.split("=")[1])
       elif arg.startswith("--help"):
           help()
       elif arg.startswith("verbose="):
           args_params["verbose"] = bool_arg_parsing(arg.split("=")[1])
       elif arg.startswith("ptrMax="):
           args_params["ptrMax"] = int(arg.split("=")[1])


    if args_params["single"]:
        run_single()
    elif args_params["reg"]:
        run_rgr()



