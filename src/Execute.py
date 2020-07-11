from Instruction import *
from FIFOQueue import *


# Used as a stage In the pipeline
class Execute:

    def __init__(self,  params=dict()):
        self.num_threads = int(params["NUM_THREAD"]) if "NUM_THREAD" in params.keys() else NUM_THREADS
        self.num_stages = int(params["NUM_STAGES"]) if "NUM_STAGES" in params.keys() else NUM_STAGES
        self.stages = FIFOQueue(self.num_stages)
        self.stages.set_q_list([Instruction.empty_inst(0)] * self.num_stages)
        # Statistics
        self.committed_inst = Instruction()
        self.count_flushed_inst = 0
        self.count_committed_inst = 0
        # Resources
        # TODO-?
        # Pointer to relevant units units
        self.thread_unit = None
        self.issue_unit = None
        self.fetch_unit = None

    # Update the information inside the execute
    def tick(self, cur_tick):
        # Save the Instruction that is committing
        self.committed_inst = self.stages.front()
        self.count_committed_inst += not self.committed_inst.empty_inst
        if (not self.committed_inst.empty_inst) and (self.committed_inst.br_taken == 1):
            self.flush()

    # Clear thread from the pipeline
    def flush(self):
        tid = self.committed_inst.tid
        next_inst_num = self.committed_inst.num + 1
        for i in range(0, self.stages.size-1):
            if (not self.stages.q_list[i].empty_inst) and (self.stages.q_list[i].tid == tid):
                self.count_flushed_inst += 1
                self.stages.q_list[i].empty_inst = True
        # Clear other units
        self.thread_unit[tid].flush()
        self.issue_unit.flush(tid)
        self.fetch_unit[tid].flush(next_inst_num)

    def done(self):
        return all([self.stages.q_list[i].empty_inst for i in range(0, self.stages.size)])

    # report the status of execute
    def get_status(self):
        q_stats = [self.stages.q_list[i].str() for i in range(0, self.num_stages)]
        msg = "{0:^50}, {1}".format(",".join(q_stats), self.committed_inst.full_str())
        return msg

    def push(self, inst):
        self.stages.push(inst)
