import pandas as pd
from Definitions import *

#This Class Dumps instructions features to a CSV file from the Fetch stage .
# If it is a branch, the branch result is written as a feature from the execute stage.
# Dumped Features:

class Dumper(): #hey david
    def __init__(self):
        self.Inst_DataSet = pd.DataFrame(columns=DUMPING_COLS)
        self.window = 0

    def Window_Dump_Append(self,Current_Window,Instruction):
        #["NAME","PC","COMPRESS","BRANCH", "BR_TAKEN","Load"]
        df_temp = pd.DataFrame([[self.window,Instruction.name, Instruction.pc,Instruction.is_comp, Instruction.is_branch,0,Instruction.is_Load]], columns=DUMPING_COLS)
        return Current_Window.append(df_temp)

    def Add_Current_Window_To_DF(self,Current_Window):
        self.Inst_DataSet = self.Inst_DataSet.append(Current_Window,ignore_index=True)
        self.window += 1
        return 0
    def PrintDF(self):
        print(self.Inst_DataSet)
    def Dump_To_CSV(self):
        path = CSV_DUMP_PATH+'/'+DUMP_NAME+'.csv'
        self.Inst_DataSet.to_csv(path)