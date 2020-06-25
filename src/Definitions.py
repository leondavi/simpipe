
SIMULATION_FILE = "../data/dummy.csv"
NUM_THREADS = 2
NUM_STAGES = 3

INSTRUCTION_SIZE = 4  # Instruction size in bytes
DEFAULT_FETCH_SIZE = 2  # Default number of instructions
DEFAULT_FETCH_QUEUE_SIZE = 3  # Instruction Queue(IQ) size
DEFAULT_PREFETCH_DELAY = 3  # The delay from the cycle it granted to received

DEFAULT_TIMEOUT = 50  # Number of ticks without instruction

# Next tasks:
#  1. Identify flushes and remove the thread from pipeline+clean fetch queue + set new ptr
#  2. Create some hazard/dependency mechanism - delay for memory instruction, long latency instruction,
#     branch stalls for hint based mechanism
#  3. WB stage- write what instruction ended - this also requires a statistic mechanism to report how many
#     instruction ended, also can write how many instruction flushed from the IQ(Good for David).
#  4. In order to do 2/3 need to create instruction analyses method
#  5. timer for end of simulation termination in case of error+end of test check
#  6. Low verbosity report for high-speed simulation
#  7. Create a mechanism that allow to transfer parameters to simulation
#  8. Organize prints (Do it as David likes).
