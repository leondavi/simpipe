import csv
import pathlib
import sys

from Definitions import *

from RegressionPermutation import *
from RunModel import *
from datetime import datetime

# Running the regression list
def run_rgr():
    now = datetime.now()
    res_filename = EXP_PREFIX+"_"+"results_"+now.strftime("%m-%d-%Y-%H_%M_%S")+".csv"
    mem_params = mem_params_from_args()

    # Extract path to where write the results of regression
    if os.path.isfile(mem_params["mem_path"]):
        mem_path = pathlib.Path(mem_params['mem_path'])
        file_path = mem_path.parents[0] / res_filename
    else:
        file_path = pathlib.Path(mem_params['mem_path']) / res_filename

    print(file_path)

    csv_file = open(file_path, 'w', newline='')
    report_writer = csv.writer(csv_file)

    rgr_db = RegressionPermutation(RGR)
    report_writer.writerow(rgr_db.key_list + ["IPC", "TICKS", "FlushedInstsWithFetchQueues","NumOfFlushes","COMMITTED_INSTS","FLUSHED_INSTS","COUNT_OF_FETCHES"])
    for perm_list in rgr_db.perm_list_of_lists:
        params_dict = dict()
        params_list = list()
        for perm in perm_list:
            key, val = perm.split(":")
            params_dict[key] = val
            params_list.append(val)
        print(params_list)
        x = RunModel(mem_params, params_dict)
        x.simulator()
        params_list.append("{0:.3f}".format(x.pipeline.ipc)) #IPC
        params_list.append(x.pipeline.last_tick) #TICKS
        params_list.append(x.pipeline.count_flushed_inst) #FlushedInstsWithFetch
        params_list.append(x.pipeline.execute_unit.num_of_flushes) #NumOfFlushes
        params_list.append(x.pipeline.execute_unit.count_committed_inst) #COMMITTED_INSTS
        params_list.append(x.pipeline.execute_unit.count_flushed_inst) #FLUSHED_INSTS
        params_list.append(x.pipeline.total_num_of_mem_access)#COUNT_OF_FETCHES

        report_writer.writerow(params_list)
        del x, params_dict, params_list

    csv_file.close()

def run_single():
    mem_params = mem_params_from_args()
    params_dict = dict()
    x = RunModel(mem_params,params_dict)
    x.simulator()
    x.report_statistics()


def mem_params_from_args():
    mem_params = MEM_DICT
    if 'dir' in args_params:
        mem_params['mem_path'] = args_params['dir']
        length = len(mem_params['mem_path'])
        i=length
        while(mem_params['mem_path'][i-1] !="\\"):
            i-=1
        Application_name = mem_params['mem_path'][i:length]
    if 'ptrMax' in args_params:
        mem_params['ptrMax'] = args_params['ptrMax']

    return mem_params


def bool_arg_parsing(input_str):
    return True if (input_str == "True" or input_str == "1") else False


def print_help():
    print("\nSimpipe Help Menu\n-------------------\n")
    print("Version: "+VERSION)
    print("<Option>=<Values>")
    print("Option           Value                Info")
    print("dir               str                 directory of csv tables OR csv file of memory")
    print("single         True/False             Running simple simulation of single run of default parameters")
    print("reg            True/False             Running regression simulation from configuration file of parameters")
    print("verbose        True/False             Pipeline verbosity")

def print_params():
    for key,val in args_params.items():
        print(key+"="+str(val),end=' ')
    print()

args_params = dict()

if __name__ == '__main__':

    args_params["single"] = False
    args_params["reg"] = False
    args_params["verbose"] = False
    args_params["csv_output"] = False
    args_params["dir"] = SIMULATION_FILE
    args_params["ptrMax"] = PTRMAX

    for arg in sys.argv[1:]:
        if arg.startswith("dir="):
            args_params["dir"] = arg.split("=")[1]
        elif arg.startswith("single="):
            args_params["single"] = bool_arg_parsing(arg.split("=")[1])
        elif arg.startswith("reg="):
            args_params["reg"] = bool_arg_parsing(arg.split("=")[1])
        elif arg.startswith("--help"):
            print_help()
        elif arg.startswith("verbose="):
            args_params["verbose"] = bool_arg_parsing(arg.split("=")[1])
        elif arg.startswith("csv_output="):
            args_params["csv_output"] = bool_arg_parsing(arg.split("=")[1])
        elif arg.startswith("ptrMax="):
            args_params["ptrMax"] = int(arg.split("=")[1])

    print_params()

    if args_params["single"]:
        run_single()
    elif args_params["reg"]:
        run_rgr()




