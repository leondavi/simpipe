# simpipe
A flexible CPU Pipeline Simulator. 


## Prerequisites:
1. Python 3.7

## Usage:

1. An example of a memory input file is located at data directory. 
2. Running a single simulation command: `python main.py dir="<Path to trace file - Memory map>" single=1
3. Running regression - multiple simulations : `python main.py dir="<Path to trace file - Memory map>" reg=1` <br>
   Define permutation of parameters under Definitions.py under section in code: `# generate permutations`
   
### Important parameters in Definitions.py:

1. PTRMAX - Set limit to the number of instrcutions that are read from memory files. 
2. NUM_THREADS - Set the number of threads.
3. NUM_STAGES - Set the number of execute stages in the pipeline. 
4. PREFETCH_DELAY - Set the number of cycles it takes to fetch line from memory. 
5. FETCH_SIZE - Number of cache lines to bring. 
6. DEAFULT_INSTRUCTION_SIZE - Instruction size in bytes 

