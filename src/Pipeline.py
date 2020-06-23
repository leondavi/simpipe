

from FIFOQueue import FIFOQueue
from Instruction import Instruction
from Definitions import *

class Fetch:
    def __init__(self,tid,Memory,fetchSize,QueueSize = DEFAULT_FETCH_QUEUE_SIZE,initMemPtr = 0,initMemEndPtr = None):
        self.tid = tid
        self.fetchQueue = FIFOQueue(QueueSize)
        self.NextInstMemPtr = initMemPtr
        self.MaxPtr = initMemEndPtr
        self.memory = Memory
        self.fetchSize = fetchSize

    def setMemPtr(self,PtrVal : int):
        self.NextInstMemPtr = PtrVal

    def fetch(self):
        if self.ptr_within_mem_range(self.NextInstMemPtr):
            curr_inst = Instruction.inst_from_row(self.memory[self.NextInstMemPtr])
            self.fetchQueue.push(curr_inst)
            self.NextInstMemPtr+=1
            return True
        return False

    def end_of_memory(self): # not within range
        return not self.ptr_within_mem_range(self.NextInstMemPtr)

    def get_Queue(self):
        return self.fetchQueue

    def ptr_within_mem_range(self,ptrVal : int):
        if self.MaxPtr:
            if (ptrVal < len(self.memory)) and (ptrVal < self.MaxPtr):
                return True
        else: #Max Ptr isn't defined
            if (ptrVal < len(self.memory)):
                return True
        return False







class Pipeline:
    ''':arg
    fetchSize - Number of instruction that fetch brings from memory each time
    '''
    def __init__(self,NumOfThreads:int,NumOfStages:int,Memory,fetchSize=1):
        self.fetchUnits = [Fetch(tid,Memory,fetchSize) for tid in range(0,NumOfThreads)]
        self.end_of_memory_fetch_list = [False] * NumOfThreads
        self.stages = FIFOQueue()
        self.stages.set_Qlist([Instruction()] * NumOfStages)
        self.NumOfThreads = NumOfThreads
        self.tid_fetch = 0
        self.fetch_policy_func = self.round_robin


    def headers_str(self):
        return ["Time"]+["Next Fetch"] + ["Q"+str(n) for n in range(0,self.NumOfThreads)] + ["IS","DE","EX","WB"]


    def tick(self):

        tid_counter = 0
        fetched = False

        self.update_end_of_memory_list()

        if not False in self.end_of_memory_fetch_list: # Checking if no more to fetch from all threads
            return False
        # select next thread to fetch by policy function
        while not fetched:
            self.tid_fetch = self.fetch_policy_func(self.tid_fetch)
            if not self.end_of_memory_fetch_list[self.tid_fetch]:
                fetched = self.fetchUnits[self.tid_fetch].fetch()
            else:
                tid_counter += 1
        if self.fetchUnits[self.tid_fetch].get_Queue().front():
            print(self.fetchUnits[self.tid_fetch].get_Queue().front().str())
        return True




    def update_end_of_memory_list(self):
        for tid in range(0,self.NumOfThreads):
            self.end_of_memory_fetch_list[tid] = self.fetchUnits[tid].end_of_memory()


    def set_fetch_policy(self,policyFunctor):
        self.fetch_policy_func = policyFunctor



    # policies
    def round_robin(self,old_val,max_val = None):
        if not max_val:
            max_val = self.NumOfThreads
        return old_val % max_val

