
class FIFOQueue:
    def __init__(self, size: int):
        self.q_list = []
        self.size = size

    def set_q_list(self, input_list: list):
        self.q_list = input_list

    def pop(self):
        if self.q_list:
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
        return self.size - self.len()

    def push(self, data):
        if len(self.q_list)+1 <= self.size:
            self.q_list.insert(0, data)
            return True
        else:
            self.q_list.insert(0, data)
            del self.q_list[-1]

    def flush(self):
        self.q_list = []

    def __bool__(self):
        return len(self.q_list) > 0