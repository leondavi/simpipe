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
        # statistics

        # anomaly
        self.anomaly_in_fetch = False
        self.anomaly_in_execute = False

    # Return True if command won't be able to execute
    # TODO - can be more sophisticate
    def got_dependency(self, inst, tick):
        return tick <= self.ready

    # Update the register with dependence
    def set_dependency(self, inst, tick, speculative):
        # In case no RD or  the target is R0 no dependency update required
        if inst.inst_opcode in ["JAL", "JALR", "BRANCH"]:
            self.ready = tick + (not speculative) * (self.num_stages - 1)
        if inst.inst_opcode == "LOAD":
            self.ready = tick + HAZARD_MEM_DELAY
        if (inst.inst_opcode in MULDIV.values()) or (inst.inst_opcode in MULDIV64.values()):
            self.ready = tick + HAZARD_MULDIV_DELAY


    # Clear any latency a register got
    def flush(self):
        self.ready_registers = [0 for _ in range(0, REGISTER_NUM)]


    def set_anomaly(self,val = True,stage = "Fetch"):
        if stage == "Fetch":
            self.anomaly_in_fetch = val
        elif stage == "Execute":
            self.anomaly_in_execute = val


    def is_anomaly(self,stage = "Fetch"):
        if stage == "Fetch":
            return self.anomaly_in_fetch
        elif stage == "Execute":
            return self.anomaly_in_execute