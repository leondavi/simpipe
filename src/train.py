from Definitions import *
from Instruction import *

# ELF

# file_path = "E:\\rv64gcc_nc_obj\\sha_riscv64uc"
#
# p = open(file_path, "rx")
# for line in p.readline():
#     print (line)
# p.close()

x = Instruction()
val = "{0:08x}".format(int("493075"))[::-1]
print(val)
x.m_inst = val
x.decode_inst()
print(x.full_str())