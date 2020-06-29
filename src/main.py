
import csv
import os
from idlelib import run
import sys

from Instruction import *
from Pipeline import Pipeline
from Definitions import *
from RegressionPermutation import *


class MainRun:

    def __init__(self, mem_path = SIMULATION_FILE,params=dict()):
        self.memory = None
        self.load_mem(mem_path)
        self.pipeline = Pipeline(self.memory[::-1], params)
        pass

    def load_mem(self, mem_path, table_prefix = DEAFULT_TABLE_PREFIX, remove_headers=True):
        csv_tables = []
        if mem_path.endswith("csv"):
            csv_tables = [mem_path]
        else: #multiple csvs
            files = os.listdir(mem_path)
            csv_files = [file for file in files if file.endswith("csv") and file.startswith(table_prefix)]

        with open(mem_path) as f:
            reader = csv.reader(f)
            self.memory = list(reader)
        if remove_headers:
            Instruction.csv_keys = {val: idx for idx, val in enumerate(self.memory[0])}
            del self.memory[0]  # Remove headers
        f.close()

    def simulator(self):
        cur_tick = 0
        while self.pipeline.tick(cur_tick):
            cur_tick += 1

        self.pipeline.report_statistics()


def run_rgr(mem_path = SIMULATION_FILE):
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

        x = MainRun(mem_path,params_dict)
        x.simulator()
        params_list.append("{0:.3f}".format(x.pipeline.ipc))
        # x.pipeline.report_model()
        print(",".join(params_list))
        del x, params_dict, params_list


def run_single(mem_path = SIMULATION_FILE):
    x = MainRun(mem_path)
    x.simulator()
    x.pipeline.ipc



def bool_arg_parsing(input_str):
    return True if (input_str == "True" or input_str == "1") else False

args_params = dict()
if __name__ == '__main__':

    args_params["single"] = False
    args_params["reg"] = False
    args_params["dir"] = SIMULATION_FILE

    for arg in sys.argv[1:]:
       if arg.startswith("dir="):
           args_params["dir"] = arg.split("=")[1]
       elif arg.startswith("single="):
           args_params["single"] = bool_arg_parsing(arg.split("=")[1])
       elif arg.startswith("reg="):
           args_params["reg"] = bool_arg_parsing(arg.split("=")[1])

    if args_params["single"]:
        run_single(args_params["dir"])
    elif args_params["reg"]:
        run_rgr(args_params["dir"])

