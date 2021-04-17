from Definitions import *
from Memory import Memory
from Decode import *

CSV_IDX_DICT = {"pc": 1, "m_inst": 5, "inst_name": 7, "br_taken": 8}
# CSV_IDX_DICT = {"tick_rec":0, "pc":1, "dpc":2, "pc_req_":3,dpc_req,m_inst,inst_grp,cname,br_taken


class Instruction:

    def __init__(self, tid=0, pc="", inst_name="x", inst_num="x", empty_inst=True):
        self.pc = pc
        self.inst_name = inst_name
        self.br_taken = 0 #
        self.m_inst = ""
        self.m_inst_hex = ""
        self.inst_grp = 0
        self.tid = tid
        self.num = inst_num
        self.empty_inst = empty_inst
        self.inst_commit = 0
        self.anomaly = 0
        # Inst fields
        self.name = "NOP"
        self.inst_opcode = "NOP"
        self.rd_vld = False
        self.rs1_vld = False
        self.rs2_vld = False
        self.rd = ""
        self.rs1 = ""
        self.rs2 = ""
        self.start_tick = None
        self.end_tick = None
        self.is_jump = False
        self.is_comp = False
        self.size_in_bytes = 0
        self.is_branch = False
        self.is_Load = False

    def str(self):
        if self.inst_name == "Bubble":
            return self.inst_name
        else:
            return "T{0}-{1}".format(self.tid, self.inst_name)

    def csv_list(self,header = False):
        if header:
            return ["pc","m_inst","inst_grp","cname","br_taken","anomaly","start_tick","end_tick"]
        return [self.pc,self.m_inst_hex,self.inst_grp,self.inst_name,self.br_taken,self.anomaly,self.start_tick,self.end_tick]

    def full_str(self):
        return "{0}-BT-{1}-E{2}-n{5}".format(self.str(), self.br_taken, self.empty(), self.m_inst[::-1], self.isa_str(), self.num) # {3} {4}

    def isa_str(self):
        return "{0},{1},{2},{3}".format(self.name, self.rd, self.rs1, self.rs2)

    def empty(self):
        return 1 if self.empty_inst else 0

    def is_branch(self):
        return self.inst_opcode in ["BRANCH"]

    def is_event(self):
        is_store = self.inst_opcode == "LOAD"
        is_branch = self.inst_opcode in ["JAL", "JALR", "BRANCH"]
        is_muldiv = (self.inst_opcode in MULDIV.values()) or (self.inst_opcode in MULDIV64.values())
        return is_store or is_branch or is_muldiv


    def __bool__(self):
        return not self.empty_inst

    def __eq__(self, other):
        return (self.pc == other.pc) and (self.tid == other.tid) and (self.m_inst == other.m_inst)

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def empty_inst(tid, name="Bubble", empty_inst=True):
        return Instruction(tid, "Z", name, "x", empty_inst)

    def delta_pc(self, inst):
        return abs(int(self.pc) - int(inst.pc))


    def inst_from_row(memory: Memory, ptr: int, tid):
        csv_row = memory.get_row(ptr)
        csv_keys = memory.get_instruction_keys()
        new_inst = Instruction()
        new_inst.empty_inst = False
        new_inst.tid = tid
        new_inst.num = ptr
        new_inst.pc = csv_row[csv_keys["pc"]]
        new_inst.inst_name = csv_row[csv_keys["cname"]]
        new_inst.br_taken = int(csv_row[csv_keys["br_taken"]])
        new_inst.m_inst = "{0:032b}".format(int(csv_row[csv_keys["m_inst"]]))[::-1]
        new_inst.m_inst_hex = csv_row[csv_keys["m_inst"]]
        new_inst.anomaly = int(csv_row[csv_keys['anomaly']] if 'anomaly' in csv_keys else False)
        #new_inst.anomaly = new_inst.br_taken # 100% accuracy
        new_inst.inst_grp = int(csv_row[csv_keys["inst_grp"]])
        # The trace not indicate on taken branches
        if (new_inst.inst_name == "jal") or (new_inst.inst_name == "jalr"):
            new_inst.anomaly = 1
            new_inst.br_taken = 1
            new_inst.is_jump = True
        decoded_inst = Decode(new_inst)  # -------------------omri added
        decoded_inst.decodeInst(new_inst)  #------------------omri added        return new_inst
        return new_inst


    @staticmethod
    def empty_inst(tid, name="Bubble", empty_inst=True):
        return Instruction(tid, "Z", name, "x", empty_inst)

    def delta_pc(self, inst):
        return abs(int(self.pc) - int(inst.pc))

    def is_anomaly(self,type = "Branch"):
        if type == "Branch":
            return  self.anomaly == 1
        if type == "Load":
            return self.anomaly == 2
        return None
        
