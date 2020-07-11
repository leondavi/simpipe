from Instruction import *


# This class is used to mange thread depends and track the status of the register
class Thread:
    # arg
    def __init__(self, tid, num_stages):
        self.tid = tid
        self.num_stages = num_stages  # Max latency till got the result
        # Used as
        self.ready_registers = [0 for _ in range(0, REGISTER_NUM)]  # TODO -?
        self.ready = 0

    # Return True if command won't be able to execute
    # TODO - can be more sophisticate
    def got_dependency(self, inst, tick):
        return tick <= self.ready

    # Update the register with dependence
    def set_dependency(self, inst, tick):
        # In case no RD or  the target is R0 no dependency update required
        if inst.inst_opcode in ["JAL", "JALR", "BRANCH"]:
            self.ready = tick + self.num_stages - 1
        if inst.inst_opcode == "LOAD":
            self.ready = tick + HAZARD_MEM_DELAY
        # TODO  MUL/DIV

    # Clear any latency a register got
    def flush(self):
        self.ready_registers = [0 for _ in range(0, REGISTER_NUM)]
