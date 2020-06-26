
# SIMULATION_FILE = "../data/dummy.csv"
SIMULATION_FILE = "../data/histtab_tid_0_ctr_0.csv"

NUM_THREADS = 2
NUM_STAGES = 3

INSTRUCTION_SIZE = 4  # Instruction size in bytes
DEFAULT_FETCH_SIZE = 4  # Default number of instructions
DEFAULT_FETCH_QUEUE_SIZE = 8  # Instruction Queue(IQ) size
DEFAULT_PREFETCH_DELAY = 3  # The delay from the cycle it granted to received

DEFAULT_TIMEOUT = -1  # Number of ticks without instruction, setting to -1 will turn it off

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
