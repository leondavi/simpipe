

CSV_IDX_DICT = {"pc": 1, "inst_name": 7, "br_taken": 8}


class Instruction:

    def __init__(self, tid=0, pc="", inst_name="x", inst_num="x", empty_inst=True):
        self.pc = pc
        self.inst_name = inst_name
        self.tid = tid
        self.num = inst_num
        self.empty_inst = empty_inst
        self.br_taken = "x"
        self.anomaly = False

    def str(self):
        return "T{0}-{1}".format(self.tid, self.inst_name)

    def full_str(self):
        return "{0}-BT-{1}-E{2}".format(self.str(), self.br_taken, self.empty())

    def empty(self):
        return 1 if self.empty_inst else 0

    def got_dependency(self):
        mem_st = self.inst_name in ["ld"]
        mem_br = self.inst_name in ["jal", "jalr", "bne", "bgeu"]
        return mem_st or mem_br

    @staticmethod
    def inst_from_row(csv_row: list, tid, num):
        new_inst = Instruction()
        new_inst.empty_inst = False
        new_inst.tid = tid
        new_inst.num = num
        for idx, val in enumerate(csv_row):
            if idx == CSV_IDX_DICT["pc"]:
                new_inst.pc = val
            elif idx == CSV_IDX_DICT["inst_name"]:
                new_inst.inst_name = val
            elif idx == CSV_IDX_DICT["br_taken"]:
                new_inst.br_taken = int(val)
        # The trace not indicate on taken branches
        if (new_inst.inst_name == "jal") or (new_inst.inst_name == "jalr"):
            new_inst.br_taken = 1
        return new_inst

    @staticmethod
    def empty_inst(tid, name="bubble", empty_inst=True):
        return Instruction(tid, "Z", name, "x", empty_inst)

    def delta_pc(self, inst):
        return abs(int(self.pc) - int(inst.pc))
