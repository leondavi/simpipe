import os


class RegressionPermutation:

    def __init__(self, list_of_lists):
        self.list_of_lists = list_of_lists
        self.perm_list_of_lists = list()
        self.key_list = list()
        self.perm_success = True
        self.gen_permutation()

    def gen_permutation(self):
        # check the rgr is in correct format
        if type(self.list_of_lists) != list:
            print("Error: RGR format not supported")
            self.perm_success = False
            return

        for lists in self.list_of_lists:
            # check that each list is in correct format
            if (type(lists) != list) or (len(lists) != 2):
                print("Error: not supported format {0}".format(lists))
                self.perm_success = False
                return

            key, values = lists
            if type(values) != list:
                values = [values]

            # if key == "RGR_WILDCARD":
            #     key = "binary"
            #     p = values[0]
            #     values = [p + "/" + s for s in os.listdir(values[0])]

            self.key_list.append(key)
            # base is empty
            if not len(self.perm_list_of_lists):
                for val in values:
                    self.perm_list_of_lists.append(["{0}:{1}".format(key, val)])
            else:
                tmp_list = list()
                for perm in self.perm_list_of_lists:
                    for val in values:
                        val = "{0}:{1}".format(key, val)
                        tmp_list.append(perm + [val])
                self.perm_list_of_lists = tmp_list
