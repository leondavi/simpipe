from Instruction import *



class BPTable:
    def __init__(self,sizeLimit = 2):
        self.sizeLimit = sizeLimit
        self.pc_set = set()
        self.data_dict = dict() # key = pc
        self.priority_to_del_list = []

    def get_data(self,pc):
        if pc in self.pc_set:
            return self.data_dict[pc]
        return None

    def add_data(self,pc,data):
        if pc not in self.pc_set:
            if len(self.pc_set) == self.sizeLimit: # in that case we need to delete
                pc_to_delete = self.priority_to_del_list[-1]
                del self.data_dict[pc_to_delete]
                self.pc_set.remove(pc_to_delete)
                del self.priority_to_del_list[-1]
            self.pc_set.add(pc)
        else:
            pc_idx = self.priority_to_del_list.index(pc)
            del(self.priority_to_del_list[pc_idx])

        self.priority_to_del_list.insert(0, pc)
        self.data_dict[pc] = data

    def len(self):
        return len(self.pc_set)


'''
---------------------> taken 
0 - Strongly not taken ---> 1 - Weakly not taken ---> 2 Weakly taken ---> 3 Strongly taken
<-------------------- not taken
'''
class BP2Bit:
    STRONGLY_NOT_TAKEN = 0
    WEAKLY_NOT_TAKEN = 1
    WEAKLY_TAKEN = 2
    STRONGLY_TAKEN = 3
    def __init__(self,table_size = 10):
        self.bp_table = BPTable(table_size)
        self.init_state = self.STRONGLY_TAKEN

    def update_branch_inst_result(self,instruction : Instruction, result_taken : bool):
        former_state = self.bp_table.get_data(instruction.pc)
        new_state = self.init_state
        if isinstance(former_state,int):
            new_state = self.next_state(former_state,result_taken)

        self.bp_table.add_data(instruction.pc,new_state)

    def get_prediction(self,instruction):
        ''':arg instruction
        returns true if branch is predicted as taken
        '''
        inst_state = self.bp_table.get_data(instruction.pc)
        if isinstance(inst_state, int):
            if inst_state >= self.WEAKLY_TAKEN:
                return True

        return False

    @staticmethod
    def next_state(current_state: int, taken: bool) -> int:
        next_state = current_state + 1 if taken else current_state - 1
        next_state = max(0, next_state)
        next_state = min(BP2Bit.STRONGLY_TAKEN, next_state)
        return next_state