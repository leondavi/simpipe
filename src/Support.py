# --------------- Policies ---------------#
def round_robin(ptr, req, size):
    for i in range(0, size):
        ptr = (ptr+1) % size
        if req[ptr]:
            return ptr
    return ptr


def lock_ptr(ptr, size):
        return (ptr - 1) % size
