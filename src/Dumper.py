import pandas as pd
from Definitions import *

#This Class Dumps instructions features to a CSV file from the Fetch stage .
# If it is a branch, the branch result is written as a feature from the execute stage.
# Dumped Features:

class Dumper(): #hey david
    def __init__(self):
        columns1 = DUMPING_COLS
        self.Inst_DataSet = pd.DataFrame(columns=columns1)

    def Window_Dump_Append(self,Current_Window,Instruction):
        df_temp = pd.DataFrame([[Instruction.name, Instruction.is_comp, Instruction.is_branch]], columns=DUMPING_COLS)
        return Current_Window.append(df_temp,ignore_index=True)

    def Add_Current_Window_To_DF(self,Current_Window):
        self.Inst_DataSet = self.Inst_DataSet.append(Current_Window)
        return 0
    def PrintDF(self):
        print(self.Inst_DataSet)
    def Dump_To_CSV(self):
        path = CSV_DUMP_PATH+'/'+DUMP_NAME+'.csv'
        self.Inst_DataSet.to_csv(path)