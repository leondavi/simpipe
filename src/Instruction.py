from Definitions import *
from Memory import Memory

CSV_IDX_DICT = {"pc": 1, "m_inst": 5, "inst_name": 7, "br_taken": 8}
# CSV_IDX_DICT = {"tick_rec":0, "pc":1, "dpc":2, "pc_req_":3,dpc_req,m_inst,inst_grp,cname,br_taken


class Instruction:

    def __init__(self, tid=0, pc="", inst_name="x", inst_num="x", empty_inst=True):
        self.pc = pc
        self.inst_name = inst_name
        self.br_taken = 0
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
        return "{0}-BT-{1}-E{2} {3} {4}".format(self.str(), self.br_taken, self.empty(), self.m_inst[::-1], self.isa_str())

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

    def decode_inst(self):
        assert self.m_inst[0:2] == "11", "Support only ILEN 32"
        opcode = (self.m_inst[0:7])[::-1]
        func3 = int((self.m_inst[12:15])[::-1], 2)
        immd_25 = int((self.m_inst[25])[::-1], 2)
        # pprint(self.inst_name, "DEBUG")
        assert opcode in OPCODE.keys(), "Unknown opcode {0}, supported RV64I ".format(opcode)
        self.inst_opcode = OPCODE[opcode]
        if self.inst_opcode == "BRANCH":
            assert func3 in BRANCH.keys(), "Unknown BRANCH func3 {0}".format(func3)
            self.name = BRANCH[func3]
        elif self.inst_opcode == "LOAD":
            assert func3 in LOAD.keys(), "Unknown LOAD func3 {0}".format(func3)
            self.name = LOAD[func3]
        elif self.inst_opcode == "STORE":
            assert func3 in STORE.keys(), "Unknown STORE func3 {0}".format(func3)
            self.name = STORE[func3]
        elif self.inst_opcode == "ALUI":
            assert func3 in ALUI.keys(), "Unknown ALUI func3 {0}".format(func3)
            self.name = ALUI[func3]
            if self.name == "SRI":
                self.name = SRI[int(self.m_inst[30])]
        elif self.inst_opcode == "ALU":
            if immd_25 == 1:
                assert func3 in MULDIV.keys(), "Unknown MULDIV func3 {0}".format(func3)
                self.name = MULDIV[func3]
            else:
                assert func3 in ALU.keys(), "Unknown ALU func3 {0}".format(func3)
                self.name = ALU[func3]
            if self.name == "ADD_SUB":
                self.name = ADD_SUB[int(self.m_inst[30])]
            elif self.name == "SR":
                self.name = SR[int(self.m_inst[30])]
        elif self.inst_opcode == "ALUIW":
            assert func3 in ALUIW.keys(), "Unknown ALUIW func3 {0}".format(func3)
            self.name = ALUIW[func3]
        elif self.inst_opcode == "ALUW":
            if immd_25 == 1:
                assert func3 in MULDIV64.keys(), "Unknown MULDIV64 func3 {0}".format(func3)
                self.inst_opcode = MULDIV64[func3]
            else:
                assert func3 in ALUW.keys(), "Unknown ALUW func3 {0}".format(func3)
                self.inst_opcode = ALUW[func3]
        else:
            self.name = self.inst_opcode
        self.decode_operands()

    def decode_operands(self):
        rd = int((self.m_inst[7:12])[::-1], 2)
        rs1 = int((self.m_inst[15:20])[::-1], 2)
        rs2 = int((self.m_inst[20:25])[::-1], 2)
        if self.inst_opcode in ["LUI", "AUIPC", "JAL", "JALR", "LOAD", "ALUI", "ALU", "ALUW", "FENCE"]:
            self.rd_vld = True
            self.rd = rd
        if self.inst_opcode in ["JALR", "BRANCH", "LOAD", "STORE", "ALUI", "ALU", "ALUW", "FENCE"]:
            self.rs1_vld = True
            self.rs1 = rs1
        if self.inst_opcode in ["BRANCH", "STORE", "ALU", "ALUW"]:
            self.rs2_vld = True
            self.rs2 = rs2

    def __bool__(self):
        return not self.empty_inst

    def __eq__(self, other):
        return (self.pc == other.pc) and (self.tid == other.tid) and (self.m_inst == other.m_inst)

    def __ne__(self, other):
        return not self == other

    @staticmethod
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
        new_inst.anomaly =  int(csv_row[csv_keys["br_taken"]])# int(csv_row[csv_keys['anomaly']] if 'anomaly' in csv_keys else False)
        new_inst.inst_grp = int(csv_row[csv_keys["inst_grp"]])
        # The trace not indicate on taken branches
        if (new_inst.inst_name == "jal") or (new_inst.inst_name == "jalr"):
            new_inst.br_taken = 1
        new_inst.decode_inst()
        return new_inst



    @staticmethod
    def empty_inst(tid, name="Bubble", empty_inst=True):
        return Instruction(tid, "Z", name, "x", empty_inst)

    def delta_pc(self, inst):
        return abs(int(self.pc) - int(inst.pc))

    def is_anomaly(self,type = "Branch"):
        return self.anomaly == 1