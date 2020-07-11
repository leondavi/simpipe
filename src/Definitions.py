from Support import *

VERSION = "1.0"

# SIMULATION_FILE = "../data/dummy.csv"
SIMULATION_FILE = "../data/histtab_tid_0_ctr_0.csv"
DEAFULT_TABLE_PREFIX = "histtab_tid_"
DEFAULT_EN_ANOMALY = False

# Simulation ARGS
NUM_THREADS = 2
NUM_STAGES = 4
SPECULATIVE = False  # [True, False] # True - keep push instructions without knowing the result
ISSUE_POLICY = "EVENT"  # ["RR", "COARSE", "EVENT","RR_ANOMALY_PERSISTENT]
PREFETCH_POLICY = "RR"  # ["RR","RR_ANOMALY"]
# Control args
VERB_ON = True
DEFAULT_TIMEOUT = 50  # Number of ticks without instruction, setting to -1 will turn it off
PTRMAX = 6300000
PTRMAX = 20
VERB_LVL = {"NONE": 0, "NORM": 1, "DEBUG": 2}
VERB = "DEBUG"  # [0,1,2]


def pprint(msg, verb="DEBUG"):
    if VERB_LVL[verb] <= VERB_LVL[VERB]:
        print(msg)


DEFAULT_INSTRUCTION_SIZE = 4  # Instruction size in bytes
IQ_SIZE = 8  # Instruction Queue(IQ) size
PREFETCH_DELAY = 3  # The delay from the cycle it granted to received
FETCH_SIZE = 4  # Default number of instructions

HAZARD_MEM_DELAY = 1
HAZARD_MULDIV_DELAY = 3
MEM_DICT = {'mem_path': SIMULATION_FILE, 'ptrMax': None}

# generate permutations
num_thread_list = [1, 2, 4, 8, 16]
issue_policy_list = ["RR", "RR_ANOMALY_PERSISTENT"]  # ["RR", "COARSE", "EVENT"]
speculative_list = [False, True]
num_stages_list = [4, 5]
prefetch_delay_list = [2, 4, 6, 8, 10]

RGR = [["NUM_THREAD", num_thread_list], ["ISSUE_POLICY", issue_policy_list],
       ["SPECULATIVE", speculative_list], ["NUM_STAGES", num_stages_list],
       ["PREFETCH_DELAY", prefetch_delay_list]]

FAST_RGR = [["NUM_THREAD", [2]], ["ISSUE_POLICY", ["RR"]], ["SPECULATIVE", [False]],
            ["NUM_STAGES", [4]], ["PREFETCH_DELAY", [3]]]

#RGR = FAST_RGR
REGISTER_NUM = 32
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
    "0011011": "ALUIW",
    "0111011": "ALUW",
    "0001111": "FENCE",
    "1110011": "ECMD",
}

BRANCH = {0: "BEQ", 1: "BNE", 4: "BLT", 5: "BGE", 6: "BLTU", 7: "BGEU"}
LOAD = {0: "LB", 1: "LH", 2: "LW", 4: "LBU", 5: "LHU", 6: "LWU", 3: "LD"}
STORE = {0: "SB", 1: "SH", 2: "SW", 3: "SD"}
ALUI = {0: "ADDI", 1: "SLLI", 2: "SLTI", 3: "SLTIU", 4: "XORI", 6: "ORI", 7: "ANDI", 1: "SLLI", 5: "SRI"}
SRI = {0: "SRLI", 1: "SRAI"}
ALU = {0: "ADD_SUB", 1: "SLL", 2: "SLT", 3: "SLTU", 4: "XOR", 5: "SR", 6: "OR", 7: "AND"}
ALUIW = {0: "ADDIW", 1: "SLLIW", 5: "SRIW"}
ALUW = {0: "ADD_SUB_W", 1: "SLLW", 5: "SRW"}

ADD_SUB = {0: "ADD", 1: "SUB"}
SR = {0: "SRL", 1: "SRA"}

MULDIV = {0: "MUL", 1: "MULH", 2: "MULHSU", 3: "MULHU", 4: "DIV", 5: "DIVU", 6: "REM", 7: "REMU"}
MULDIV64 = {0: "MULW", 4: "DIVW", 5: "DIVUW", 6: "REMW", 7: "REMUW"}

# Extra
#  - Check how many instructions were flushed when using different mechanisms
#  - Timer for end of simulation termination in case of error+end of test check
#  - print - simulation progress every tick cycles - [YE]
#  - Change verbosity method to level sensitive - [YE]
#  - print to CSV pipeline, and rgr
#  - Anomaly detection influence inside the pipeline - [David]


