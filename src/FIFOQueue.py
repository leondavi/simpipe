


class FIFOQueue():
    def __init__(self,size="inf"):
        self.Qlist = []
        self.size = size

    def set_Qlist(self,input_list : list):
        self.Qlist = input_list

    def pop(self):
        if self.Qlist:
            tmp = self.Qlist[-1]
            del self.Qlist[-1]
            return tmp

    def len(self):
        return len(self.Qlist)

    def push(self,data):
        '''
        retur True if succeed and False if list passed the allowed size
        '''
        if len(self.Qlist)+1 < self.size:
            self.Qlist.insert(0,data)
            return True
        else:
            self.Qlist.insert(0,data)
            del self.Qlist[-1]



