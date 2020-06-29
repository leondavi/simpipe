VERSION = "1.0"

# SIMULATION_FILE = "../data/dummy.csv"
SIMULATION_FILE = "../data/histtab_tid_0_ctr_0.csv"
DEAFULT_TABLE_PREFIX = "histtab_tid_"

NUM_THREADS = 4
NUM_STAGES = 4
SPECULATIVE = True  # [True, False]
ISSUE_POLICY = "RR"  # ["RR", "COARSE", "EVENT"]
VERB_ON = True

DEFAULT_INSTRUCTION_SIZE = 4  # Instruction size in bytes
IQ_SIZE = 8  # Instruction Queue(IQ) size
PREFETCH_DELAY = 3  # The delay from the cycle it granted to received
FETCH_SIZE = 4  # Default number of instructions

DEFAULT_TIMEOUT = -1  # Number of ticks without instruction, setting to -1 will turn it off

OPCODE = {
    "0110111": "LUI",
    "0010111": "AUIPC",
    "1101111": "JAL",
    "1100111": "JALR",
    "1100011": "BRANCH",
    "0000011": "LOAD",
    "0100011": "STORE",
    "0010011": "ALUI",
    "0110011": "ALU",
    "0011011": "ALUW",
    "0001111": "FENCE",
    "1110011": "ECMD"
}

BRANCH = {0: "BEQ", 1: "BNE", 4: "BLT", 5: "BGE", 6: "BLTU", 7: "BGEU"}
LOAD = {0: "LB", 1: "LH", 2: "LW", 4: "LBU", 5: "LHU", 6: "LWU", 3: "LD"}
STORE = {0: "SB", 1: "SH", 2: "SW", 3: "SD"}
ALUI = {0: "ADDI", 1: "SLLI", 2: "SLTI", 3: "SLTIU", 4: "XORI", 6: "ORI", 7: "ANDI", 1: "SLLI", 5: "SRI"}
SRI = {0: "SRLI", 1: "SRAI"}
ALU = {0: "ADD_SUB", 1: "SLL", 2: "SLT", 3: "SLTU", 4: "XOR", 5: "SR", 6: "OR", 7: "AND"}
ADD_SUB = {0: "ADD", 1: "SUB"}
SR = {0: "SRL", 1: "SRA"}

# Next tasks:
#  1. Identify flushes and remove the thread from pipeline+clean fetch queue + set new ptr                      DONE
#  2. Create some hazard/dependency mechanism - delay for memory instruction, long latency instruction,
#     branch stalls for hint based mechanism                                                            ONGOING-see(3)
#  3. WB stage- write what instruction ended - this also requires a statistic mechanism to report how many
#     instruction ended, also can write how many instruction flushed from the IQ(Good for David).       ONGOING-see(4)
#  4. In order to do 2/3 need to create instruction analyses method                                     ONGOING-see(5)
#  5. timer for end of simulation termination in case of error+end of test check
#  6. Low verbosity report for high-speed simulation
#  7. Create a mechanism that allow to transfer parameters to simulation
#  8. Organize prints (Do it as David likes).
# 06.26
#  1. need to inverse the csv + load a pieces of application - currently I flip the memory
#  2. Add inst num, to follow the branch scenario                                                                DONE
#  3. Need to extract all branch scenarios
#  4. Create some statistic report in the end
#  5. run some test - and extract all branch based on taken bit.
