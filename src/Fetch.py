from FIFOQueue import FIFOQueue
from Instruction import *
from Definitions import *
from Memory import Memory
from BTB import BTB


class Fetch:

    def __init__(self, tid: int, memory : Memory, params, thread_unit):
        self.tid = tid
        self.thread_unit = thread_unit
        self.queue_size = int(params["IQ_SIZE"]) if "IQ_SIZE" in params.keys() else IQ_SIZE
        self.fetchQueue = FIFOQueue(self.queue_size)
        self.initMemPtr = self.thread_unit.arch_inst_num
        self.NextInstMemPtr = self.initMemPtr
        self.MaxPtr = memory.len()
        self.memory = memory
        self.fetch_size = int(params["FETCH_SIZE"]) if "FETCH_SIZE" in params.keys() \
            else FETCH_SIZE  # Max number of instructions to fetch from memory
        # PreFetch scheduling mechanism
        self.prefetch_ongoing = False
        self.flush_ongoing = False
        self.prefetch_delay = int(params["PREFETCH_DELAY"]) if "PREFETCH_DELAY" in params.keys() \
            else PREFETCH_DELAY
        self.prefetch_cycle = 0
        # Statistics
        self.prefetch_inst_count = 0
        self.flushed_inst_count = 0
        self.dummy_inst_count = 0
        self.prefetch_ae =  params["PREFETCH_AE"] == "True" if "PREFETCH_AE" in params.keys() else PREFETCH_AE
        self.bp_en = params["BP_EN"] == "True" if "BP_EN" in params.keys() else BP_EN
        self.num_of_mem_access = 0
        self.branch_taken_in_queue = False
        self.load_in_queue = False
        self.btb = BTB(self.memory,tid,BTB_TABLE_SIZE)

    def set_mem_ptr(self, ptr_val: int):
        self.NextInstMemPtr = ptr_val

    def fetch_stats_update(self,inst):
        self.NextInstMemPtr += 1
        self.prefetch_inst_count += 1
        self.branch_taken_in_queue |= inst.is_anomaly("Branch")
        self.load_in_queue |= inst.is_anomaly("Load")
        if self.prefetch_ae and inst.is_anomaly("Branch"):
            return False
        if self.bp_en:
            if inst.is_branch():
                self.btb.update(inst,inst.is_anomaly(type="Branch"))
            btb_res = self.btb.predict(inst)
            if btb_res != self.btb.NOT_FOUND:
                self.NextInstMemPtr = btb_res
                return False
        return True


    def fetch(self,cur_tick):

        # Check that the address is valid.
        if not self.ptr_within_mem_range(self.NextInstMemPtr):
            return False

        # First instruction must be pushed and update the pointers
        first_inst = Instruction.inst_from_row(self.memory, self.NextInstMemPtr, self.tid)
        first_inst.start_tick = cur_tick
        self.fetchQueue.push(first_inst)
        if not self.fetch_stats_update(first_inst):
            return  # break the fetch due to branch
        # Calculate based on the current offset where the instruction located in the line
        max_fetch_size = int(self.fetch_size - ((int(first_inst.pc) / DEFAULT_INSTRUCTION_SIZE) % self.fetch_size) - 1)

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
                    if not self.fetch_stats_update(curr_inst):
                        return # break the fetch due to branch
                    former_inst = curr_inst

            # None were pushed, create an empty instruction
            if empty_inst:
                dummy_inst = Instruction.empty_inst(self.tid, "dummy", False)
                dummy_inst.pc = str(int(first_inst.pc)+4*(i+1))
                self.fetchQueue.push(dummy_inst)
                self.dummy_inst_count += 1

            self.fetchQueue.back().start_tick = cur_tick


        return True

    # Progress pre-fetching, checks if got pending fetch request, and the fetch delay is passed.
    def tick(self, cur_tick):
        if self.prefetch_ongoing and (self.prefetch_cycle + self.prefetch_delay <= cur_tick):
            if not self.flush_ongoing:
                self.fetch(cur_tick)
            self.flush_ongoing = False
            self.prefetch_ongoing = False

    # Change fetch status
    def set_prefetch(self, cur_tick):
        self.num_of_mem_access += 1
        self.prefetch_ongoing = True
        self.prefetch_cycle = cur_tick
        self.flush_ongoing = False

    # return if allowed to schedule for pre-fetching
    def check_prefetch(self):
        # Check if there is already prefetch ongoing, or all instruction are done
        if self.prefetch_ongoing or self.mem_done():
            return False
        # anomaly case
        if self.prefetch_ae and self.branch_taken_in_queue:
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
        return self.mem_done() and (not self.prefetch_ongoing)

    def flush(self, next_num):
        numOfInst_to_flush = self.fetchQueue.len()
        self.flushed_inst_count += self.fetchQueue.len()
        self.fetchQueue.flush()
        self.NextInstMemPtr = next_num
        self.flush_ongoing = True
        self.branch_taken_in_queue = False
        self.load_in_queue = False
        return numOfInst_to_flush

    def report_statistics(self):
        print("Fetch TID={0} prefetch_inst_count={1} dummy_count={2} flushed_inst={3} mem_len={4} " 
              "mem_delay={5} next_ptr={6} btb_success={7} btb_falseAlarm={8}".format(self.tid, self.prefetch_inst_count, self.dummy_inst_count,
                                                  self.flushed_inst_count, self.memory.len(), self.prefetch_delay,
                                                  self.NextInstMemPtr,self.btb.get_success_rate(),self.btb.get_false_alram_rate()))

    def get_ae_in_queue(self):
        return (self.branch_taken_in_queue or self.load_in_queue) and (not self.fetchQueue.empty())


    def dummy_btb(self,inst):
        return 0