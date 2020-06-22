

from FIFOQueue import FIFOQueue
from Instruction import Instruction
from Definitions import *

class Fetch:
    def __init__(self,tid,Memory,fetchSize,QueueSize = DEFAULT_FETCH_QUEUE_SIZE,pc = 0):
        self.tid = tid
        self.fetchQueues = FIFOQueue(QueueSize)
        self.nextPc = pc
        self.memory = Memory
        self.fetchSize = fetchSize

        inst = Instruction.inst_from_row(Memory[0])
        print(inst.str())

    def set_pc(self,pc):
        self.nextPc = pc


class Pipeline:
    ''':arg
    fetchSize - Number of instruction that fetch brings from memory each time
    '''
    def __init__(self,NumOfThreads:int,NumOfStages:int,Memory,fetchSize=1):
        self.fetch = [Fetch(tid,Memory,fetchSize) for tid in range(0,NumOfThreads)]
        self.stages = FIFOQueue()
        self.stages.set_Qlist([Instruction()] * NumOfStages)
        self.NumOfThreads = NumOfThreads

    def headers_str(self):
        return ["Time"]+["Next Fetch"] + ["Q"+str(n) for n in range(0,self.NumOfThreads)] + ["IS","DE","EX","WB"]




