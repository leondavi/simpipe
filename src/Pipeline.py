from Fetch import *


class Pipeline:
    # arg
    # fetch_size - Number of instruction that fetch brings from memory each time
    def __init__(self, memory, num_threads=NUM_THREADS, num_stages=NUM_STAGES, fetch_size=DEFAULT_FETCH_SIZE,
                 issue_policy=ISSUE_POLICY):
        self.fetchUnits = [Fetch(tid, memory, fetch_size) for tid in range(0, num_threads)]  # Create fetch unit
        self.stages = FIFOQueue(num_stages)
        self.stages.set_q_list([Instruction.empty_inst(0)] * num_stages)
        self.wb_inst = Instruction.empty_inst(0)
        self.num_threads = num_threads
        self.issue_policy = issue_policy
        self.tid_issue_ptr = 0
        self.tid_prefetch_vld = False
        self.tid_prefetch_ptr = 0
        self.dependency_status = [0 for _ in range(0, num_threads)]
        self.fetch_policy_func = self.round_robin
        self.timer = DEFAULT_TIMEOUT  # TODO Create timer in case no instruction are done for some latency
        # Statistics
        self.inst_committed = 0

    def headers_str(self):  # TODO - update the pipe EX as the remain instruction,WB=last commit/dropped inst from queue
        return ["Time"]+["Next Fetch"] + ["Q"+str(n) for n in range(0, self.num_threads)] + ["IS", "DE", "EX", "WB"]

    def print_tick(self, cur_tick):
        q_sts = [str(self.fetchUnits[i].fetchQueue.len()) for i in range(0, self.num_threads)]
        p_inst = [self.stages.q_list[i].str() for i in range(0, self.stages.size)]
        p_id = self.tid_prefetch_ptr if self.tid_prefetch_vld else "x"
        print("{0:<5},{1:^5},{2:^8},{3:^30},{4} {5} {6}".format(
            cur_tick, p_id, ",".join(q_sts), ",".join(p_inst), self.wb_inst.full_str(), self.wb_inst.num ,
            self.wb_inst.pc))

    def tick(self, cur_tick):
        # Checking if all threads finished there fetching
        if self.check_done():
            return False

        # Select with thread will prefetch
        self.set_prefetch(cur_tick)

        # Select with thread will issue
        self.set_issue(cur_tick)

        # commit the instruction
        self.set_commit()

        # Update dependency
        self.update_dependency(cur_tick)

        # Update simulation statistics
        self.update_statistics(cur_tick)

        # Progress Fetch
        for idx in range(0, self.num_threads):
            self.fetchUnits[idx].tick(cur_tick)

        self.timer -= 1

        self.print_tick(cur_tick)
        return True

    # Check Between all thread, who is legit for fetching
    def set_prefetch(self, cur_tick):
        self.tid_prefetch_vld = False
        req_list = [self.fetchUnits[i].check_prefetch() for i in range(self.num_threads)]
        self.tid_prefetch_ptr = self.round_robin(self.tid_prefetch_ptr, req_list, self.num_threads)
        if req_list[self.tid_prefetch_ptr]:
            self.fetchUnits[self.tid_prefetch_ptr].set_prefetch(cur_tick)
            self.tid_prefetch_vld = True

    # Select between all thread who is next to issue his instruction
    def set_issue(self, cur_tick):
        # Check with queue got instructions
        fetch_list = [self.fetchUnits[i].fetchQueue.len() != 0 for i in range(0, self.num_threads)]
        # Check if there are some dependency
        dependency_list = self.get_dependency(cur_tick)
        # Merge the two vectors above
        req_list = [fetch_list[i] and dependency_list[i] for i in range(0, self.num_threads)]
        # update based on the policy
        self.update_issue_policy()
        # Select issue thread
        self.tid_issue_ptr = self.round_robin(self.tid_issue_ptr, req_list, self.num_threads)
        self.wb_inst = self.stages.front()

        if req_list[self.tid_issue_ptr]:
            inst = self.fetchUnits[self.tid_issue_ptr].fetchQueue.pop()
            self.stages.push(inst)
        else:  # Push empty inst
            self.stages.push(Instruction.empty_inst(0))

    def set_commit(self):
        inst = self.stages.front()
        if inst.br_taken == 1:
            self.flush_pipe(inst.tid, inst.num)

    def update_dependency(self, cur_tick):
        inst = self.stages.back()
        if inst.got_dependency() and (not SPECULATIVE):
            self.dependency_status[inst.tid] = cur_tick+self.stages.size

    def get_dependency(self, cur_tick):
        return [self.dependency_status[i] <= cur_tick for i in range(0, self.num_threads)]

    def update_statistics(self, cur_tick):
        # count how many valid instruction committed
        self.last_tick = cur_tick
        if not self.wb_inst.empty_inst:
            self.inst_committed += 1

    def report_statistics(self):
        print("Inst Committed {0} ipc {1:.3f}".format(self.inst_committed, float(self.inst_committed/self.last_tick)))

    def flush_pipe(self, tid, cur_num):
        for i in range(0, self.stages.size-1):
            if self.stages.q_list[i].tid == tid:
                self.stages.q_list[i].empty_inst = True
        self.fetchUnits[tid].flush_fetch(cur_num+1)

    def update_issue_policy(self):
        if ISSUE_POLICY == "EVENT":
            self.event_policy()
        elif ISSUE_POLICY == "COARSE":
            self.coarse_policy()
        elif ISSUE_POLICY == "RR":
            pass

    def event_policy(self):
        if self.fetchUnits[self.tid_issue_ptr].fetchQueue.len() != 0:
            next_inst = self.fetchUnits[self.tid_issue_ptr].fetchQueue.front()
            if next_inst.got_dependency():
                print("EVENT TEST")
                self.tid_issue_ptr = (self.tid_issue_ptr-1) % self.num_threads

    def coarse_policy(self):
        self.tid_issue_ptr = (self.tid_issue_ptr - 1) % self.num_threads

    # policies
    @staticmethod
    def round_robin(ptr, req, size):
        for i in range(0, size):
            ptr = (ptr+1) % size
            if req[ptr]:
                return ptr
        return ptr

    def check_done(self):
        # Check all fetch units are done = last inst + no pending inst + queue is empty
        fetch_done = all([self.fetchUnits[i].fetch_done() for i in range(0, self.num_threads)])
        # Check pipe stage empty
        stages_done = all([self.stages.q_list[i].empty_inst for i in range(0, self.stages.size)])
        timeout_done = self.timer == 0
        return (fetch_done and stages_done) or timeout_done
