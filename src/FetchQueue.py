from Instruction import *
class FetchQueue:
    def __init__(self, size_bytes: int):
        self.q_list = []
        self.free_bytes=size_bytes
        self.max_bytes = size_bytes

    def set_q_list(self, input_list: list):
        self.q_list = input_list

    def pop(self):
        if self.q_list:
            self.free_bytes+=self.q_list[-1].size_in_bytes
            tmp = self.q_list[-1]
            del self.q_list[-1]

            return tmp

    def front(self):  # returns first out
        if self.q_list:
            return self.q_list[-1]
        return None

    def back(self):
        if self.q_list:
            return self.q_list[0]
        return None

    def at(self,idx):
        if idx < len(self.q_list):
            return self.q_list[idx]
        return None

    def len(self):
        return len(self.q_list)

    def space(self):
        return self.free_bytes

    def push(self, data):
        if self.free_bytes>=data.size_in_bytes:
            self.q_list.insert(0, data)
            self.free_bytes-=data.size_in_bytes
            return True
        else:
            self.q_list.insert(0, data)
            del self.q_list[-1]

    def flush(self):
        self.q_list = []
        self.free_bytes = self.max_bytes

    def __bool__(self):
        return len(self.q_list) > 0

    def empty(self):
        return len(self.q_list) == 0