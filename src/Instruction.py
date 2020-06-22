


class Instruction:

    def __init__(self,tid=-1,pc="",opcode="",attributes="",inpipe=False):
        self.pc = pc
        self.opcode = opcode
        self.attributes = attributes
        self.tid = tid
        self.inpipe = False
