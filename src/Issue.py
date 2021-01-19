from Instruction import *
from Fetch import Fetch

# Used as a stage In the pipeline
class Issue:
    def __init__(self,  params=dict()):
        self.num_threads = int(params["NUM_THREAD"]) if "NUM_THREAD" in params.keys() else NUM_THREADS
        self.issue_policy = params["ISSUE_POLICY"] if "ISSUE_POLICY" in params.keys() else ISSUE_POLICY
        self.speculative = params["SPECULATIVE"] == "True" if "SPECULATIVE" in params.keys() else SPECULATIVE
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
    def tick(self, cur_tick):
        # Check if there is an instruction in issue and try push it into execute
        if not self.issue_empty:
            self.push_inst(cur_tick)
        else:
            self.execute_unit.push(Instruction.empty_inst(0))

        # Check if the current instruction is issued, if so, schedule for next cycle
        if self.issue_empty:
            self.schedule_inst(cur_tick)

    # Check if issue need to be cleared in case of flush
    def flush(self, tid):
        if (not self.issue_empty) and (self.issue_inst.tid == tid):
            self.count_flushed_inst += 1
            self.issue_empty = True
            self.issue_inst.empty_inst = 1
            return True
        return False

    # report the status of execute
    def get_status(self):
        issue_inst = Instruction.empty_inst(0) if self.issue_empty else self.issue_inst
        msg = "{0}".format(issue_inst.str())
        return msg

    # Check if the next instruction can be pushed
    def push_inst(self, tick):
        tid = self.issue_inst.tid
        if not self.thread_unit[tid].got_dependency(self.issue_inst, tick):
            self.thread_unit[tid].set_dependency(self.issue_inst, tick, self.speculative)  # TODO -what is the latency
            self.execute_unit.push(self.issue_inst)
            self.issue_empty = True
        else:
            self.execute_unit.push(Instruction.empty_inst(0))

    def get_fetch_list(self,cur_tick):
        thread_dependency_list = [self.thread_unit[tid].got_dependency("", cur_tick+1) for tid in range(0, self.num_threads)]
        fetch_queues_len_list = [(self.fetch_unit[tid].fetchQueue.len()  > 0) for tid in range(0, self.num_threads)]
        combined_fetch_list = [fetch_queues_len_list[tid] and (not thread_dependency_list[tid]) for tid in range(0, self.num_threads)]

        if sum(fetch_queues_len_list) == 1:
            return fetch_queues_len_list

        if self.issue_policy == "EVENT":
            return combined_fetch_list
        elif self.issue_policy == "EVENT_AE":
            return combined_fetch_list
        elif self.issue_policy == "COARSE":
            return combined_fetch_list
        elif self.issue_policy == "RR":
            pass

        return fetch_queues_len_list

    def schedule_inst(self, cur_tick):
        fetch_list = self.get_fetch_list(cur_tick)
        self.update_policy(cur_tick)
        self.issue_ptr = round_robin(self.issue_ptr, fetch_list, self.num_threads)

        if fetch_list[self.issue_ptr]:
            self.issue_inst = self.fetch_unit[self.issue_ptr].fetchQueue.pop()
            self.issue_empty = False
        else:  # Push empty inst
            self.issue_inst = Instruction.empty_inst(0)
            self.issue_empty = True

    # --------------- Policies ---------------#

    def update_policy(self, cur_tick):
        if self.issue_policy == "EVENT":
            self.event_policy(cur_tick)
        elif self.issue_policy == "EVENT_AE":
            self.event_ae_policy(cur_tick)
        elif self.issue_policy == "COARSE":
            self.coarse_policy(cur_tick)
        elif self.issue_policy == "RR":
            pass

    def coarse_policy(self,cur_tick):
        inst_ev = self.execute_unit.stages.at(1)
        if inst_ev and inst_ev.br_taken:
            return
        # if self.execute_unit.stages.back().is_event(): # check if first stage in execute is event
        #     return
        self.issue_ptr = lock_ptr(self.issue_ptr, self.num_threads)

    # Event - next instruction
    def event_policy(self, cur_tick):
        if self.fetch_unit[self.issue_ptr].fetchQueue.len() != 0:
            next_inst = self.fetch_unit[self.issue_ptr].fetchQueue.front()
            # check if next cycle the instruction will pass Issue
            if next_inst.is_event() and (not self.thread_unit[self.issue_ptr].got_dependency(next_inst, cur_tick)):
                self.issue_ptr = lock_ptr(self.issue_ptr, self.num_threads)

    # Event AE - next instruction
    def event_ae_policy(self, cur_tick):
        if self.fetch_unit[self.issue_ptr].fetchQueue.len() != 0:
            next_inst = self.fetch_unit[self.issue_ptr].fetchQueue.front()
            # check if next cycle the instruction will pass Issue
            if self.fetch_unit[self.issue_ptr].get_ae_in_queue() and (not self.thread_unit[self.issue_ptr].got_dependency(next_inst, cur_tick)):
                self.issue_ptr = lock_ptr(self.issue_ptr, self.num_threads)


    def report_model(self):
        print("Issue Thread_num={0} Issue_policy={1} speculative={2} flushed={3}"
              .format(self.num_threads, self.issue_policy, self.speculative, self.count_flushed_inst))

