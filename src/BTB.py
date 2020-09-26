from Memory import *
from Instruction import Instruction

class BPTable:
    def __init__(self,sizeLimit = 2):
        self.sizeLimit = sizeLimit
        self.pc_set = set()
        self.data_dict = dict() # key = pc
        self.priority_to_del_list = []

    def get_data(self,pc):
        if pc in self.pc_set:
            self.touch_pc(pc) #push to front
            return self.data_dict[pc]
        return None

    def touch_pc(self,pc):
        '''
        Updates priority list when pc is requested
        '''
        pc_idx = self.priority_to_del_list.index(pc)
        del self.priority_to_del_list[pc_idx]
        self.priority_to_del_list.insert(0, pc)  # pu

    def add_data(self,pc,data):
        if pc not in self.pc_set:
            if len(self.pc_set) == self.sizeLimit: # in that case we need to delete
                pc_to_delete = self.priority_to_del_list[-1]
                del self.data_dict[pc_to_delete]
                self.pc_set.remove(pc_to_delete)
                del self.priority_to_del_list[-1]
            self.pc_set.add(pc)
            self.priority_to_del_list.insert(0, pc)
        else:
            self.touch_pc(pc)

        self.data_dict[pc] = data

    def len(self):
        return len(self.pc_set)

class BTB:

    def __init__(self,memory : Memory, tid, table_size = 10):
        self.bp_table = BPTable(table_size)
        self.memory = memory
        self.tid = tid

    def update(self,inst : Instruction):
        curr_inst_num = inst.num
        next_inst_num = curr_inst_num + 1
        if next_inst_num < self.memory.len():
            next_inst = Instruction.inst_from_row(self.memory, curr_inst_num+1 , self.tid)
            target_pc = next_inst.pc
            inst_pc = inst.pc
            self.bp_table.add_data(inst_pc,target_pc)

    NOT_FOUND = 0
    WRONG_PC = 0
    def predict(self,inst):
        target_pc = self.bp_table.get_data(inst.pc)
        if target_pc is not None:
            curr_inst_num = inst.num
            next_inst_num = curr_inst_num + 1
            if next_inst_num < self.memory.len():
                next_inst = Instruction.inst_from_row(self.memory, curr_inst_num + 1, self.tid)
                if next_inst.pc == target_pc:
                    return next_inst_num
                else:
                    return BTB.WRONG_PC
        return BTB.NOT_FOUND
