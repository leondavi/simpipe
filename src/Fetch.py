from FIFOQueue import FIFOQueue
from Instruction import *
from Definitions import *
from Memory import Memory


class Fetch:

    def __init__(self, tid: int, memory : Memory, params):
        self.tid = tid
        self.queue_size = int(params["IQ_SIZE"]) if "IQ_SIZE" in params.keys() else IQ_SIZE
        self.fetchQueue = FIFOQueue(self.queue_size)
        self.initMemPtr = 0
        self.NextInstMemPtr = self.initMemPtr
        self.MaxPtr = memory.len()
        self.memory = memory
        self.fetch_size = int(params["FETCH_SIZE"]) if "FETCH_SIZE" in params.keys() \
            else FETCH_SIZE  # Max number of instructions to fetch from memory
        # PreFetch scheduling mechanism
        self.prefetch_ongoing = False
        self.prefetch_delay = int(params["PREFETCH_DELAY"]) if "PREFETCH_DELAY" in params.keys() \
            else PREFETCH_DELAY
        self.prefetch_cycle = 0
        # Statistics
        self.prefetch_inst_count = 0
        self.flushed_inst_count = 0
        self.dummy_inst_count = 0
        self.anomaly_enabled = params['en_anomaly']
        self.anomaly_flag = False

    def set_mem_ptr(self, ptr_val: int):
        self.NextInstMemPtr = ptr_val

    def fetch(self):

        # Check that the address is valid.
        if not self.ptr_within_mem_range(self.NextInstMemPtr):
            return False

        # First instruction must be pushed and update the pointers
        first_inst = Instruction.inst_from_row(self.memory, self.NextInstMemPtr, self.tid)
        self.fetchQueue.push(first_inst)
        self.NextInstMemPtr += 1
        self.prefetch_inst_count += 1

        # Calculate based on the current offset where the instruction located in the line
        max_fetch_size = self.fetch_size - ((int(first_inst.pc) / DEFAULT_INSTRUCTION_SIZE) % self.fetch_size) - 1

        former_inst = first_inst  # Used inside the loop to track last instruction
        empty_inst = False  # Once set, the rest instruction that pushed are empty

        # Looping over all possible left instruction can be pulled.
        for i in range(0, int(max_fetch_size)):
            # Check if next address is valid
            if not self.ptr_within_mem_range(self.NextInstMemPtr):
                empty_inst = True
            else:
                curr_inst = Instruction.inst_from_row(self.memory, self.NextInstMemPtr, self.tid)
                delta_pc = curr_inst.delta_pc(former_inst)
                # Check that next instruction is sequential in memory
                if delta_pc != DEFAULT_INSTRUCTION_SIZE:
                    empty_inst = True
                else:
                    self.fetchQueue.push(curr_inst)
                    self.NextInstMemPtr += 1
                    self.prefetch_inst_count += 1
                    former_inst = curr_inst

            # None were pushed, create an empty instruction
            if empty_inst:
                self.fetchQueue.push(Instruction.empty_inst(self.tid, "dummy", False))
                self.dummy_inst_count += 1

        return True

    # Progress pre-fetching, checks if got pending fetch request, and the fetch delay is passed.
    def tick(self, cur_tick):
        if self.prefetch_ongoing and (self.prefetch_cycle + self.prefetch_delay <= cur_tick):
            self.fetch()
            self.prefetch_ongoing = False

    # Change fetch status
    def set_prefetch(self, cur_tick):
        self.prefetch_ongoing = True
        self.prefetch_cycle = cur_tick

    # return if allowed to schedule for pre-fetching
    def check_prefetch(self):
        # Check if there is already prefetch ongoing, or all instruction are done
        if self.prefetch_ongoing or self.mem_done():
            return False
        # anomaly case
        if self.anomaly_logic():
            print("tid"+str(self.tid)+" Anomaly")
            return False
        # Make sure in case schedule that got space for store all received instructions
        return self.fetchQueue.space() >= self.fetch_size

    def ptr_within_mem_range(self, ptr_val: int):
        if self.initMemPtr > ptr_val:
            return False
        if self.MaxPtr:
            if (ptr_val < self.memory.len()) and (ptr_val < self.MaxPtr):
                return True
        else:  # Max Ptr isn't defined
            if ptr_val < self.memory.len():
                return True
        return False

    def mem_done(self):
        return self.NextInstMemPtr >= self.MaxPtr

    def fetch_done(self):
        return self.mem_done() and (not self.prefetch_ongoing) and (self.fetchQueue.len() == 0)

    def flush_fetch(self, next_num):
        self.flushed_inst_count += self.fetchQueue.len()
        self.fetchQueue.flush()
        self.NextInstMemPtr = next_num
        self.prefetch_ongoing = False  # TODO - maybe wait for old ongoing fetch to be done?

    def report_statistics(self):
        print("Fetch TID={0} prefetched_inst_count={1} dummy_count={2} flushed_inst={3} mem_len={4} mem_delay={5} next_ptr={6}".format(
            self.tid, self.prefetch_inst_count, self.dummy_inst_count,self.flushed_inst_count, self.memory.len(), self.prefetch_delay,
            self.NextInstMemPtr))

    #anomaly functions

    def anomaly_logic(self):
        if not self.anomaly_enabled:
            return False

        self.set_anomaly(self.anomaly_check())
        return self.anomaly_flag

    def set_anomaly(self,val = True):
        self.anomaly_flag = val

    #whil anomaly appears in queue then there is anomaly
    def anomaly_check(self):
        found_inst = Instruction()
        for i in range(0,int(self.fetchQueue.len()/2)):
            if self.fetchQueue.at(i).anomaly:
                found_inst = self.fetchQueue.at(i)
                self.last_anomaly_inst = found_inst
                return True
        self.last_anomaly_inst = found_inst
        return False