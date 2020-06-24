from gettext import c2py

from FIFOQueue import FIFOQueue
from Instruction import *
from Definitions import *
from Fetch import *


class Pipeline:
    ''':arg
    fetchSize - Number of instruction that fetch brings from memory each time
    '''
    def __init__(self, NumOfThreads:int, NumOfStages:int, memory, fetchSize=DEFAULT_FETCH_SIZE):
        self.fetchUnits = [Fetch(tid, memory, fetchSize) for tid in range(0, NumOfThreads)]
        self.end_of_memory_fetch_list = [False] * NumOfThreads
        self.stages = FIFOQueue(NumOfStages)
        self.stages.set_q_list([Instruction()] * NumOfStages)
        self.NumOfThreads = NumOfThreads
        self.tid_issue_ptr = 0
        self.tid_prefetch_vld = False
        self.tid_prefetch_ptr = 0
        self.fetch_policy_func = self.round_robin
        self.timer = 50  # TODO - YE remove it

    def headers_str(self):
        return ["Time"]+["Next Fetch"] + ["Q"+str(n) for n in range(0, self.NumOfThreads)] + ["IS", "DE", "EX", "WB"]

    def print_tick(self, cur_tick):
        q_sts = [str(self.fetchUnits[i].fetchQueue.len()) for i in range(0, self.NumOfThreads)]
        p_inst = [self.stages.q_list[i].str() for i in range(0, self.stages.size)]
        p_id = self.tid_prefetch_ptr if self.tid_prefetch_vld else "x"
        print("{0:<5},{1:^5},{2},{3}".format(cur_tick, p_id, ",".join(q_sts), ",".join(p_inst)))

    def tick(self, cur_tick):
        # Checking if all threads finished there fetching
        self.update_end_of_memory_list()
        if all(self.end_of_memory_fetch_list):
            return False

        # Select with thread will prefetch
        self.set_prefetch(cur_tick)

        # Select with thread will issue
        self.set_issue(cur_tick)

        # Progress Fetch
        for idx in range(0, self.NumOfThreads):
            self.fetchUnits[idx].tick(cur_tick)
        if self.timer == 0:
            return False
        self.timer -= 1

        self.print_tick(cur_tick)
        return True

    # Check Between all thread, who is legit for fetching
    def set_prefetch(self, cur_tick):
        self.tid_prefetch_vld = False
        req_list = [self.fetchUnits[i].check_prefetch() for i in range(self.NumOfThreads)]
        self.tid_prefetch_ptr = self.round_robin(self.tid_prefetch_ptr, req_list, self.NumOfThreads)
        if req_list[self.tid_prefetch_ptr]:
            self.fetchUnits[self.tid_prefetch_ptr].set_prefetch(cur_tick)
            self.tid_prefetch_vld = True

    # Select between all thread who is next to issue his instruction
    def set_issue(self, cur_tick):
        req_list = [self.fetchUnits[i].fetchQueue.len() != 0 for i in range(self.NumOfThreads)]
        self.tid_issue_ptr = self.round_robin(self.tid_issue_ptr, req_list, self.NumOfThreads)
        if req_list[self.tid_issue_ptr]:
            inst = self.fetchUnits[self.tid_issue_ptr].fetchQueue.pop()
            self.stages.push(inst)

    def update_end_of_memory_list(self):
        for tid in range(0, self.NumOfThreads):
            self.end_of_memory_fetch_list[tid] = self.fetchUnits[tid].end_of_memory()

    def set_fetch_policy(self, policyFunctor):
        self.fetch_policy_func = policyFunctor

    # policies
    def round_robin(self, ptr, req, size):
        for i in range(0, size):
            ptr = (ptr+1) % size
            if req[ptr]:
                return ptr
        return ptr

