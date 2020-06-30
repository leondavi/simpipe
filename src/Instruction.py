from Definitions import *
from Memory import Memory

CSV_IDX_DICT = {"pc": 1,"m_inst":5, "inst_name": 7, "br_taken": 8}
# CSV_IDX_DICT = {"tick_rec":0, "pc":1, "dpc":2, "pc_req_":3,dpc_req,m_inst,inst_grp,cname,br_taken


class Instruction:

    def __init__(self, tid=0, pc="", inst_name="x", inst_num="x", empty_inst=True):
        self.pc = pc
        self.inst_name = inst_name
        self.br_taken = "x"
        self.m_inst = ""
        self.tid = tid
        self.num = inst_num
        self.empty_inst = empty_inst
        self.anomaly = False
        # Inst fields
        self.name = "NOP"
        self.inst_opcode = "NOP"
        self.rd_vld = False
        self.rs1_vld = False
        self.rs2_vld = False
        self.rd = ""
        self.rs1 = ""
        self.rs2 = ""

    def str(self):
        return "T{0}-{1}".format(self.tid, self.inst_name)

    def full_str(self):
        return "{0}-BT-{1}-E{2} {3} {4}".format(self.str(), self.br_taken, self.empty(), self.m_inst[::-1], self.isa_str())

    def isa_str(self):
        return "{0},{1},{2},{3}".format(self.name, self.rd, self.rs1, self.rs2)

    def empty(self):
        return 1 if self.empty_inst else 0

    def got_dependency(self):
        #is_store = self.inst_opcode == "LOAD"
        is_store = False
        is_branch = self.inst_opcode in ["JAL", "JALR", "BRANCH"]
        return is_store or is_branch

    def decode_inst(self):
        assert self.m_inst[0:2] == "11", "Support only ILEN 32"
        opcode = (self.m_inst[0:7])[::-1]
        func3 = int((self.m_inst[12:15])[::-1], 2)
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
            assert func3 in ALU.keys(), "Unknown ALU func3 {0}".format(func3)
            self.name = ALU[func3]
            if self.name == "ADD_SUB":
                self.name = ADD_SUB[int(self.m_inst[30])]
            elif self.name == "SR":
                self.name = SR[int(self.m_inst[30])]
        elif self.inst_name == "ALUWI":
            assert 0 # TODO - not suportted yet
        elif self.inst_name == "ALUW":
            assert 0  # TODO - not suportted yet
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

    @staticmethod
    def inst_from_row(memory : Memory, ptr : int, tid):
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
        # The trace not indicate on taken branches
        if (new_inst.inst_name == "jal") or (new_inst.inst_name == "jalr"):
            new_inst.br_taken = 1
        new_inst.decode_inst()
        return new_inst

    @staticmethod
    def empty_inst(tid, name="bubble", empty_inst=True):
        return Instruction(tid, "Z", name, "x", empty_inst)

    def delta_pc(self, inst):
        return abs(int(self.pc) - int(inst.pc))
