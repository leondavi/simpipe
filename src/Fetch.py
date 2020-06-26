from FIFOQueue import FIFOQueue
from Instruction import *
from Definitions import *


class Fetch:

    def __init__(self, tid: int, memory, fetch_size, queue_size=DEFAULT_FETCH_QUEUE_SIZE,
                 prefetch_delay=DEFAULT_PREFETCH_DELAY, init_mem_ptr=0):
        self.tid = tid
        self.fetchQueue = FIFOQueue(queue_size)
        self.NextInstMemPtr = init_mem_ptr
        self.MaxPtr = len(memory)
        self.initMemPtr = init_mem_ptr
        self.memory = memory
        self.fetch_size = fetch_size  # Max number of instructions to fetch from memory
        # PreFetch scheduling mechanism
        self.prefetch_ongoing = False
        self.prefetch_delay = prefetch_delay
        self.prefetch_cycle = 0

    def set_mem_ptr(self, ptr_val: int):
        self.NextInstMemPtr = ptr_val

    def fetch(self):

        # Check that the address is valid.
        if not self.ptr_within_mem_range(self.NextInstMemPtr):
            return False

        # First instruction must be pushed and update the pointers
        first_inst = Instruction.inst_from_row(self.memory[self.NextInstMemPtr], self.tid, self.NextInstMemPtr)
        self.fetchQueue.push(first_inst)
        self.NextInstMemPtr += 1

        # Calculate based on the current offset where the instruction located in the line
        max_fetch_size = self.fetch_size - ((int(first_inst.pc)/INSTRUCTION_SIZE) % self.fetch_size) - 1

        former_inst = first_inst  # Used inside the loop to track last instruction
        empty_inst = False  # Once set, the rest instruction that pushed are empty

        # Looping over all possible left instruction can be pulled.
        for i in range(0, int(max_fetch_size)):
            # Check if next address is valid
            if not self.ptr_within_mem_range(self.NextInstMemPtr):
                empty_inst = True
            else:
                curr_inst = Instruction.inst_from_row(self.memory[self.NextInstMemPtr], self.tid, self.NextInstMemPtr)
                delta_pc = curr_inst.delta_pc(former_inst)
                # Check that next instruction is sequential in memory
                if delta_pc != INSTRUCTION_SIZE:
                    empty_inst = True
                else:
                    self.fetchQueue.push(curr_inst)
                    self.NextInstMemPtr += 1
                    former_inst = curr_inst

            # None were pushed, create an empty instruction
            if empty_inst:
                self.fetchQueue.push(Instruction.empty_inst(self.tid, "dummy", False))

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
        # Make sure in case schedule that got space for store all received instructions
        return self.fetchQueue.space() >= self.fetch_size

    def ptr_within_mem_range(self, ptr_val: int):
        if self.initMemPtr > ptr_val:
            return False
        if self.MaxPtr:
            if (ptr_val < len(self.memory)) and (ptr_val < self.MaxPtr):
                return True
        else:  # Max Ptr isn't defined
            if ptr_val < len(self.memory):
                return True
        return False

    def mem_done(self):
        return self.NextInstMemPtr >= self.MaxPtr

    def fetch_done(self):
        return self.mem_done() and (not self.prefetch_ongoing) and (self.fetchQueue.len() == 0)

    def flush_fetch(self, next_num):
        self.fetchQueue.flush()
        self.NextInstMemPtr = next_num
        self.prefetch_ongoing = False  # TODO - maybe wait for old ongoing fetch to be done?
