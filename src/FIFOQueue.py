


class FIFOQueue():
    def __init__(self,size="inf"):
        self.Qlist = []
        self.size = size

    def pop(self):
        if self.Qlist:
            last = self.Qlist[-1]
            del self.Qlist[-1]
            return last

    def push(self,data):
        '''
        retur True if succeed and False if list passed the allowed size
        '''
        if len(self.Qlist)+1 < self.size:
            self.Qlist.append(data)
            return True
        else:
            return False


