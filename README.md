# simpipe
A flexible CPU Pipeline Simulator. 


## Prerequisites:
1. Python 3.7

## Usage:

1. An example of a memory input file is located at data directory. 
2. Running a single simulation command: `python main.py dir="<Path to trace file - Memory map>" single=1
3. Running regression - multiple simulations : `python main.py dir="<Path to trace file - Memory map>" reg=1` <br>
   Define permutation of parameters under Definitions.py under section in code: `# generate permutations`
