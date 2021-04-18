from Definitions import *
from Instruction import *





x = Instruction()
val = "{0:08x}".format(int("493075"))[::-1]
print(val)
x.m_inst = val
x.decode_inst()
print(x.full_str())