from Thread import *
from Fetch import *
from Issue import *
from Execute import *
from Memory import Memory


class Pipeline:
    # arg
    def __init__(self, memory: Memory, params=dict()):
        self.num_threads = int(params["NUM_THREAD"]) if "NUM_THREAD" in params.keys() else NUM_THREADS
        self.num_stages = int(params["NUM_STAGES"]) if "NUM_STAGES" in params.keys() else NUM_STAGES
        self.thread_unit = [Thread(tid, self.num_stages) for tid in range(0, self.num_threads)]
        self.fetch_unit = [Fetch(tid, memory, params) for tid in range(0, self.num_threads)]  # Create fetch unit
        self.issue_unit = Issue(params)
        self.execute_unit = Execute(params)
        self.connect()
        self.timer = DEFAULT_TIMEOUT
        # Prefetch
        self.prefetch_policy = params["PREFETCH_POLICY"] if "PREFETCH_POLICY" in params.keys() else PREFETCH_POLICY
        self.tid_prefetch_vld = False
        self.tid_prefetch_ptr = 0
        # Verbosity
        self.timer = DEFAULT_TIMEOUT
        # Statistics
        self.last_tick = 0
        self.count_flushed_inst = 0
        self.ipc = 0

    # Connect between the class's
    def connect(self):

        # Fetch Unit
        for tid in range(0,self.num_threads):
            self.fetch_unit[tid].thread_unit = self.thread_unit

        # Issue Unit
        # - thread_unit - Checks thread info and dependency
        # - fetch_unit - check the instruction inside the fetch
        # - Execute - pass the instruction to execute unit
        self.issue_unit.thread_unit = self.thread_unit
        self.issue_unit.fetch_unit = self.fetch_unit
        self.issue_unit.execute_unit = self.execute_unit

        # Execute
        # - thread_unit - TBD
        # - issue_unit - update in case of flush
        # - fetch_unit - update in case of flush
        self.execute_unit.thread_unit = self.thread_unit
        self.execute_unit.issue_unit = self.issue_unit
        self.execute_unit.fetch_unit = self.fetch_unit

    # The main function that happens every cycle and responsible on the progress of the pipeline.
    def tick(self, cur_tick):
        # Checking if all threads and units are finished there execution
        if self.check_done():
            return False

        # Update Execute
        self.execute_unit.tick(cur_tick)

        # Update Issue
        self.issue_unit.tick(cur_tick)

        # Select which thread will prefetch
        self.set_prefetch(cur_tick)

        # Progress Fetch
        for idx in range(0, self.num_threads):
            self.fetch_unit[idx].tick(cur_tick)

        # Update simulation statistics
        self.update_statistics(cur_tick)

        self.trace_tick(cur_tick)
        return True

    # Used as trace of simulator
    def trace_tick(self, cur_tick):
        prefetch_id = self.tid_prefetch_ptr if self.tid_prefetch_vld else "x"
        fetch_sts = [str(self.fetch_unit[i].fetchQueue.len()) for i in range(0, self.num_threads)]
        issue_sts = self.issue_unit.get_status()
        execute_sts = self.execute_unit.get_status()
        thread_sts = [" t"+str(i)+": "+str(self.thread_unit[i].ready)+","+str(int(self.thread_unit[i].anomaly)) for i in range(0, self.num_threads)]
        msg = "{0:<5},{1:^5},{2},{3:^15}, {4:^35} \t, {5}".format(
            cur_tick, prefetch_id, ",".join(fetch_sts), issue_sts, execute_sts, ",".join(thread_sts))
        pprint(msg, "NORM")

    # Check Between all thread, who is legit for fetching
    def set_prefetch(self, cur_tick):
        self.tid_prefetch_vld = False
        req_list = [self.fetch_unit[tid].check_prefetch() for tid in range(self.num_threads)]
        # update based on the policy of prefetch - changes tid_prefetch_ptr if it is needed
        self.update_prefetch_policy()
        self.tid_prefetch_ptr = round_robin(self.tid_prefetch_ptr, req_list, self.num_threads)
        if req_list[self.tid_prefetch_ptr]:
            self.fetch_unit[self.tid_prefetch_ptr].set_prefetch(cur_tick)
            self.tid_prefetch_vld = True

    # --------------- Policies ---------------#
    def update_prefetch_policy(self):
        if self.prefetch_policy == "RR_ANOMALY":
            self.round_robin_anomaly_policy()
        elif self.prefetch_policy == "RR":
            pass

    def round_robin_anomaly_policy(self):
        ''':arg
         finds an empty fetch queue that is not in an anomaly state
         and set it to next fetch if no anomaly
        '''

        tmp_ptr = self.tid_prefetch_ptr
        for tid in range(0,self.num_threads):
            tmp_ptr = (tmp_ptr + 1) % self.num_threads
            valid = not self.fetch_unit[tmp_ptr].fetchQueue and\
            not self.fetch_unit[tmp_ptr].fetch_done and\
            not self.thread_unit[tmp_ptr].is_anomaly()
            if valid:
                self.tid_prefetch_ptr = (tmp_ptr-1) % self.num_threads
                return

    # Check if all units are done
    def check_done(self):
        # Check all fetch units are done = last inst + no pending inst + queue is empty
        fetch_done = all([self.fetch_unit[i].fetch_done() for i in range(0, self.num_threads)])
        issue_done = self.issue_unit.issue_empty
        execute_done = self.execute_unit.done()
        timeout_done = self.timer == 0
        return (fetch_done and issue_done and execute_done) or timeout_done

    # ---------------  Statistics ---------------#

    def update_statistics(self, cur_tick):
        # count how many valid instruction committed
        self.timer -= 1
        self.last_tick = cur_tick
        if not self.execute_unit.committed_inst.empty_inst:
            self.timer = DEFAULT_TIMEOUT
        else:
            self.timer -= 1

        if self.last_tick:  # Avoid division by zero
            self.ipc = float(self.execute_unit.count_committed_inst / self.last_tick)

        self.count_flushed_inst = self.issue_unit.count_flushed_inst + self.execute_unit.count_flushed_inst +\
            sum([self.fetch_unit[idx].flushed_inst_count for idx in range(0, self.num_threads)])

    def report_model(self):
        for tid_idx in range(0, self.num_threads):
            self.fetch_unit[tid_idx].report_statistics()
        self.issue_unit.report_model()
        self.execute_unit.report_model()
        print("Num Thread={0}, stage={1}".format(
            self.num_threads, self.execute_unit.num_stages))

    def report_statistics(self):
        msg = "Inst Committed {0} ipc {1:.3f} flushed {2}".format(
            self.execute_unit.count_committed_inst, self.ipc, self.count_flushed_inst)
        pprint(msg, "NONE")
