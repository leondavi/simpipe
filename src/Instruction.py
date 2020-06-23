

CSV_IDX_DICT = {"pc":1,"inst_name":7,"br_taken":8}


class Instruction:

    def __init__(self,tid=-1,pc="",inst_name="",attributes="",emptyInst=False):
        self.pc = pc
        self.inst_name = inst_name
        self.attributes = attributes
        self.tid = tid
        self.emptyInst = emptyInst
        self.br_taken = False
        self.anomaly = False

    def str(self):
        return "TH"+str(self.tid)+"-"+self.inst_name

    def empty(self):
        return self.emptyInst

    @staticmethod
    def inst_from_row(csv_row : list,tid = 0):
        new_inst = Instruction()
        for idx,val in enumerate(csv_row):
            if idx == CSV_IDX_DICT["pc"]:
                new_inst.pc = val
            elif idx == CSV_IDX_DICT["inst_name"]:
                new_inst.inst_name = val
            elif idx == CSV_IDX_DICT["br_taken"]:
                new_inst.br_taken = val
        return new_inst

    @staticmethod
    def empty_inst(tid):
        return Instruction(tid,"","","",True)

    def delta_pc(self,inst):
        return abs(self.pc - inst.pc)



