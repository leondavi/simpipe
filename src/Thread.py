from Instruction import *


# This class is used to mange thread depends and track the status of the register
class Thread:
    # arg
    def __init__(self, tid, params=dict()):
        self.tid = tid
        self.num_stages = int(params["NUM_STAGES"]) if "NUM_STAGES" in params.keys() else NUM_STAGES
        self.forward_en =  params["FORWARD_EN"] == "True" if "FORWARD_EN" in params.keys() else FORWARD_EN
        self.issue_policy = params["ISSUE_POLICY"] if "ISSUE_POLICY" in params.keys() else ISSUE_POLICY
        # Used as
        self.ready_registers = [0 for _ in range(0, REGISTER_NUM)]  # TODO -?
        self.ready = 0
        # statistics

    # Return True if command won't be able to execute
    # TODO - can be more sophisticate
    def got_dependency(self, inst, tick):
        return tick <= self.ready

    # Update the register with dependence
    def set_dependency(self, inst, tick, speculative):
        # In case no RD or  the target is R0 no dependency update required
        if inst.inst_opcode in ["JAL", "JALR", "BRANCH"] :
            if  self.issue_policy == "EVENT_AE" :
                if inst.is_anomaly():
                    self.ready = tick + (not speculative) * (self.num_stages - 1)
            else:
                self.ready = tick + (not speculative) * (self.num_stages - 1)
        if inst.inst_opcode == "LOAD":
            self.ready = tick + ( HAZARD_MEM_DELAY if self.forward_en else (self.num_stages - 1))
        if (inst.inst_opcode in MULDIV.values()) or (inst.inst_opcode in MULDIV64.values()):
            self.ready = tick + (HAZARD_MULDIV_DELAY if self.forward_en else (self.num_stages - 1))


    # Clear any latency a register got
    def flush(self):
        self.ready_registers = [0 for _ in range(0, REGISTER_NUM)]
