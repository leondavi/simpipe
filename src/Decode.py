from Definitions import *
from Instruction import *
import json
class Decode(): #hey david

    def __init__(self,instruction):
        instruction.opcode = (instruction.m_inst[0:7])[::-1]            #leftovers from old decode logic
        instruction.func3 = int((instruction.m_inst[12:15])[::-1], 2)   #leftovers from old decode logic
        instruction.immd_25 = int((instruction.m_inst[25])[::-1], 2)    #leftovers from old decode logic
        instruction.m_inst=instruction.m_inst

#   Decode fields -  gets an instruction and json arr an returns 2 arrays:
#1. fields: the registers (and imm for non compressed instructions) that this instruction uses (example: ["rd","rs1","rs2"])
#2. values: the values of fields. (for example: if fields is the same like last example, so values=[1,2,3] means that
#           rd=1 rs1=2 rs2=3
    def decodeFields(self, inst, arr):
        fields = arr['fields']
        values = [0] * len(fields)
        for i in range(len(fields)):
            cur_field_bit_range = arr[fields[i]]
            values[i] = inst[cur_field_bit_range[0]:cur_field_bit_range[1] + 1]
            #
            if(values[i]):
                values[i] = int(values[i], 2)
        return values, fields

#   decodeInst - gets an instruction and filles its following attributes:
#   1. name
#   2. used registers

    def decodeInst(self, instruction):
        with open('riscv_isa.json') as f:   #open json
            arr_tmp = json.load(f)
        last = False    #when we get to a leaf last=true
        comp = 1        #compressed instruction
        if (instruction.m_inst[1] == "0" and instruction.m_inst[0] == "0"): #compressed quardrad0
            arr_tmp = arr_tmp["00"]
        if (instruction.m_inst[1] == "0" and instruction.m_inst[0] == "1"): #compressed quardrad1
            arr_tmp = arr_tmp["01"]
        if (instruction.m_inst[1] == "1" and instruction.m_inst[0] == "0"): #compressed quardrad2
            arr_tmp = arr_tmp["10"]
        if (instruction.m_inst[1] == "1" and instruction.m_inst[0] == "1"): #non-compressed
            arr_tmp = arr_tmp["11"]
            comp = 0

        while (last == 0):       # decending down the decoding tree until last leve/ leaf
            last = arr_tmp['last_level']
            if last==0:
                bit_range = arr_tmp['bit_range']
                if(len(bit_range)>1):
                    next_field = instruction.m_inst[bit_range[0]:bit_range[1] + 1]
                else:
                    next_field = instruction.m_inst[bit_range[0]]
                next_field = str(next_field)
                if(next_field[::-1] not in arr_tmp):
                    arr_tmp=arr_tmp['else']
                else:
                    arr_tmp = arr_tmp[next_field[::-1]]

        values, fields = self.decodeFields(instruction.m_inst, arr_tmp)
        instruction.name=arr_tmp['name']
        for i in range(len(fields)):
            if (fields[i]=='rd'):
                instruction.rd=values[i]
            elif (fields[i]=='rs1'):
                instruction.rs1=values[i]
            elif (fields[i]=='rs2'):
                instruction.rs2=values[i]