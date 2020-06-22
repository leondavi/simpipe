

from FIFOQueue import FIFOQueue
from Instruction import Instruction


class Fetch:
    def __init__(self,tid,QueueSize,Memory,pc = 0):
        self.tid = tid
        self.fetchQueues = FIFOQueue(QueueSize)
        self.pc = pc
        self.memory = Memory

    def set_pc(self,pc):
        self.pc = pc


class Pipeline:
    def __init__(self,NumOfThreads:int,NumOfStages:int,Memory):
        self.fetch = [Fetch(tid,Memory) for tid in range(0,NumOfThreads)]
        self.stages = FIFOQueue()
        self.stages.set_Qlist([Instruction()] * NumOfStages)




