
import csv
import os
from idlelib import run

from Instruction import *
from Pipeline import Pipeline
from Definitions import *
from RegressionPermutation import *


class MainRun:

    def __init__(self, params=dict()):
        self.memory = None
        self.load_mem()
        self.pipeline = Pipeline(self.memory[::-1], params)
        pass

    def load_mem(self, memory_file=SIMULATION_FILE, remove_headers=True):
        with open(memory_file) as f:
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


def run_rgr():
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

        x = MainRun(params_dict)
        x.simulator()
        params_list.append("{0:.3f}".format(x.pipeline.ipc))
        # x.pipeline.report_model()
        print(",".join(params_list))
        del x, params_dict, params_list


def run_single():
    x = MainRun()
    x.simulator()
    x.pipeline.ipc


#run_single()
run_rgr()


