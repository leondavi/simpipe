import numpy as np
from numpy import *
import AE_Definitions
from AE_Definitions import *
import torch

class DataOrganizor:
    def __init__(self,Path):
        self.Path = Path
        self.RawDataSet = torch.tensor(genfromtxt(self.Path, delimiter=',')[:,0:FEATURES+NOT_NEEDED_FEATURES])
        self.windowSizesCol = self.RawDataSet[:,9].tolist()
        self.PCCol = self.RawDataSet[:,3].tolist()
        #Normalizing Values
        self.RawDataSet[:, 9] = self.RawDataSet[:, 9]/8  #Normalize Window Size
        #take labeled anomaly value
        self.anomalyCol = self.RawDataSet[:,11]
        self.anomalyCol = self.anomalyCol.tolist()
        #remove first features (NOT_NEEDED_FEATURES)
        self.RawDataSet = self.RawDataSet[:,NOT_NEEDED_FEATURES+1:NOT_NEEDED_FEATURES+FEATURES_WITHOUT_PC+1]

        #PC to Binary
        self.PCColToBin()                                #PC to 32 bits

        self.CurWindowIndex = 0
        self.CurWindowSize = 0
        self.FirstIdxInCurWindow = 1

# cat the PC binary values to Raw Dataset
    def PCColToBin(self):
        NewPCCol = [0]*len(self.PCCol)
        for i in range(1,len(self.PCCol)-1):
            NewPCCol[i] = self.PCToBinary32List(int(self.PCCol[i]))
        NewPCCol[0] = [0]*32
        b = np.array(NewPCCol)
        b[len(b)-1] = [0]*32
        b = np.vstack(b[:]).astype(np.float)
        c = torch.from_numpy(b)
        #TODO  - FIX THE CAT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.RawDataSet = torch.cat((self.RawDataSet,c), dim=-1)
        return NewPCCol

#change the pc value from 1 integer feature to 32 binary features
    def PCToBinary32List(self,PC):
        PCBin = [int(x) for x in bin(PC)[2:]]
        PCBin  = [0 for _ in range(32 - len(PCBin))] + PCBin #padd with zeros
        return PCBin

    def getNextWindow(self):
        # Exporting the current window size
        self.CurWindowSize =int(self.windowSizesCol[self.FirstIdxInCurWindow])
        # The Next Window Set Of Instructions FEATURES X MAX_INST_IN_WINDOW
        CurWindowSet = torch.Tensor([[0 for i in range(FEATURES)]for k in range (MAX_INST_IN_WINDOW)])
        # Exporting the current window from RawDataSet to the CurWindowSet according to the window index
        CurWindowSet[0:self.CurWindowSize,:] = self.RawDataSet[self.FirstIdxInCurWindow:(self.FirstIdxInCurWindow+self.CurWindowSize),:]
        # forward the index of the next owindow first instruction
        self.FirstIdxInCurWindow += self.CurWindowSize
        # forward the index of the next window
        self.CurWindowIndex += 1
        return CurWindowSet


Data1 = DataOrganizor(r"C:\Users\omrir\Desktop\University\Project\Dumps\FFT\‏‏FFT_COMP_100k - Analyzed.csv")
for i in range (20):
    CurSet = Data1.getNextWindow()
    print(CurSet.tolist()[0][0:6])
print(1)