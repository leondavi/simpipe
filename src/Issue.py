from Instruction import *


# Used as a stage In the pipeline
class Issue:
    def __init__(self,  params=dict()):
        self.num_threads = int(params["NUM_THREAD"]) if "NUM_THREAD" in params.keys() else NUM_THREADS
        self.issue_policy = params["ISSUE_POLICY"] if "ISSUE_POLICY" in params.keys() else ISSUE_POLICY
        self.issue_ptr = 0
        self.issue_empty = True  # Indication if got pending instruction
        self.issue_inst = Instruction()
        # Statistic
        self.count_flushed_inst = 0
        # Pointer to relevant units units
        self.thread_unit = None
        self.fetch_unit = None
        self.execute_unit = None

    # Tick issue state
    # Check if there exists an instruction in issue, if the instruction can be executed push it
    # into next unit.
    # After that, check if the instruction is pushed, if so, schedules the next one.
    def tick(self, tick):
        # Check if there is an instruction in issue and try push it into execute
        if not self.issue_empty:
            self.push_inst(tick)
        else:
            self.execute_unit.push(Instruction.empty_inst(0))

        # Check if the current instruction is issued, if so, schedule for next cycle
        if self.issue_empty:
            self.schedule_inst()

    # Check if issue need to be cleared in case of flush
    def flush(self, tid):
        if (not self.issue_empty) and (self.issue_inst.tid == tid):
            self.count_flushed_inst += 1
            self.issue_empty = True

    # report the status of execute
    def get_status(self):
        issue_inst = Instruction.empty_inst(0) if self.issue_empty else self.issue_inst
        msg = "{0}".format(issue_inst.str())
        return msg

    # Check if the next instruction can be pushed
    def push_inst(self, tick):
        tid = self.issue_inst.tid
        if not self.thread_unit[tid].got_dependency(self.issue_inst, tick):
            self.thread_unit[tid].set_dependency(self.issue_inst, tick)  # TODO -what is the latency
            self.execute_unit.push(self.issue_inst)
            self.issue_empty = True
        else:
            self.execute_unit.push(Instruction.empty_inst(0))

    def schedule_inst(self):
        fetch_list = [self.fetch_unit[tid].fetchQueue.len() for tid in range(0, self.num_threads)]
        self.update_policy()
        self.issue_ptr = round_robin(self.issue_ptr, fetch_list, self.num_threads)

        if fetch_list[self.issue_ptr]:
            self.issue_inst = self.fetch_unit[self.issue_ptr].fetchQueue.pop()
            self.issue_empty = False
        else:  # Push empty inst
            self.issue_inst = Instruction.empty_inst(0)
            self.issue_empty = True

    # --------------- Policies ---------------#

    def update_policy(self):
        if self.issue_policy == "EVENT":
            self.event_policy()
        elif self.issue_policy == "COARSE":
            self.coarse_policy()
        elif self.issue_policy == "RR_ANOMALY_PERSISTENT":
            self.round_robin_anomaly_persistent_policy()
        elif self.issue_policy == "RR":
            pass

    # Coarse - save the pointer on the same spot
    def coarse_policy(self):
        self.issue_ptr = (self.issue_ptr - 1) % self.num_threads

    # Event - next instruction
    def event_policy(self):
        if self.fetchUnits[self.issue_ptr].fetchQueue.len() != 0:
            next_inst = self.fetchUnits[self.issue_ptr].fetchQueue.front()
            # check if next cycle the instruction will pass Issue
            if next_inst.is_event():  # TODO - create is event
                self.coarse_policy()

