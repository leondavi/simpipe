from Memory import *
from Instruction import Instruction

STATE_STORNGEST_TAKEN = 3
STATE_WEAKLY_TAKEN = 2
STATE_WEAKLY_NOT_TAKEN = 1
STATE_STRONGEST_NOT_TAKEN = 0
def update_2bits_state(state: int, taken):
    return min(STATE_STORNGEST_TAKEN, state + 1) if taken else max(STATE_STRONGEST_NOT_TAKEN, state - 1)

def predict_2bits(curr_state : int) -> int:
    return curr_state > STATE_WEAKLY_NOT_TAKEN

class BPAttribute:
    def __init__(self,target_pc,bits_state = STATE_STORNGEST_TAKEN,miss_count = 0):
        self.target_pc = target_pc
        self.bits_state = bits_state
        self.miss_count = miss_count

    NUMBER_OF_MISSES_TO_DECIDE_OPPOSITE = 5
    def miss_count_decision(self):
        return self.miss_count > self.NUMBER_OF_MISSES_TO_DECIDE_OPPOSITE

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

    def touch_pc(self,pc,br_taken = None):
        '''
        Updates priority list when pc is requested
        '''
        pc_idx = self.priority_to_del_list.index(pc)
        del self.priority_to_del_list[pc_idx]
        self.priority_to_del_list.insert(0, pc)  # pu
        if br_taken is not None:
            self.data_dict[pc].bits_state = update_2bits_state( self.data_dict[pc].bits_state,br_taken) # updating 2 bits state

    def add_data(self,pc,target_pc,br_taken):
        if pc not in self.pc_set:
            if len(self.pc_set) == self.sizeLimit: # in that case we need to delete
                pc_to_delete = self.priority_to_del_list[-1]
                del self.data_dict[pc_to_delete]
                self.pc_set.remove(pc_to_delete)
                del self.priority_to_del_list[-1]
            self.pc_set.add(pc)
            self.data_dict[pc] = BPAttribute(target_pc,STATE_WEAKLY_TAKEN)
            self.priority_to_del_list.insert(0, pc)
        else:
            self.touch_pc(pc,br_taken)

    def len(self):
        return len(self.pc_set)

class BTB:

    def __init__(self,memory : Memory, tid, table_size = 10):
        self.bp_table = BPTable(table_size)
        self.memory = memory
        self.tid = tid
        self.success_count = 0
        self.false_alarm_count = 0
        self.total_predictions = 0

    def validator_ex(self,inst:Instruction):
        if inst.pc in self.bp_table.pc_set:
            if predict_2bits(self.bp_table.data_dict[inst.pc].bits_state) == inst.br_taken:
                self.bp_table.data_dict[inst.pc].miss_count = 0
            else:
                self.bp_table.data_dict[inst.pc].miss_count += 1

    def update(self,inst : Instruction, branch_taken_decision):
        curr_inst_num = inst.num
        next_inst_num = curr_inst_num + 1
        if next_inst_num < self.memory.len():
            next_inst = Instruction.inst_from_row(self.memory, curr_inst_num+1 , self.tid)
            target_pc = next_inst.pc
            inst_pc = inst.pc
            self.bp_table.add_data(inst_pc,target_pc,branch_taken_decision)

    NOT_FOUND = -1
    WRONG_PC = 0
    def predict(self,inst):
        attribute = self.bp_table.get_data(inst.pc)
        if attribute is not None:
            self.total_predictions += 1
            target_pc = attribute.target_pc
            two_bits_prediction = predict_2bits(attribute.bits_state)
            miss_count_flag = attribute.miss_count_decision()
            curr_inst_num = inst.num
            next_inst_num = curr_inst_num + 1
            prediction_final = (not two_bits_prediction) if miss_count_flag else two_bits_prediction
            # prediction_final = inst.is_anomaly("Branch")
            if prediction_final == bool(inst.br_taken):
                self.success_count += 1
            if prediction_final == (not bool(inst.br_taken)):
                self.false_alarm_count += 1
            if next_inst_num < self.memory.len():
                next_inst = Instruction.inst_from_row(self.memory, curr_inst_num + 1, self.tid)
                if (next_inst.pc == target_pc) and prediction_final:
                    return next_inst_num
                else:
                    return BTB.WRONG_PC
        return self.NOT_FOUND

    def get_success_rate(self):
        return self.success_count/self.total_predictions

    def get_false_alram_rate(self):
        return self.false_alarm_count/self.total_predictions

