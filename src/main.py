import csv
import pathlib
import sys

from Definitions import *

from RegressionPermutation import *
from RunModel import *


def run_rgr():
    mem_params = mem_params_from_args()
    if os.path.isfile(mem_params["mem_path"]):
        mem_path = pathlib.Path(mem_params['mem_path'])
        file_path = mem_path.parents[0] / "results.csv"
    else:
        file_path = mem_params['mem_path'] + "\\results.csv"

    print(file_path)

    csv_file = open(file_path, 'w', newline='')
    report_writer = csv.writer(csv_file)

    rgr_db = RegressionPermutation(RGR)
    report_writer.writerow(rgr_db.key_list + ["IPC"])
    for perm_list in rgr_db.perm_list_of_lists:
        params_dict = dict()
        params_list = list()
        for perm in perm_list:
            key, val = perm.split(":")
            params_dict[key] = val
            params_list.append(val)
        print(params_list)
        params_dict = update_pipeline_params(params_dict) #update with attributes from user input
        x = RunModel(mem_params, params_dict)
        x.simulator()
        params_list.append("{0:.3f}".format(x.pipeline.ipc))

        report_writer.writerow(params_list)
        del x, params_dict, params_list

    csv_file.close()

def update_pipeline_params(params_dict : dict):
    params_dict['en_anomaly'] = args_params["en_anomaly"]
    return params_dict

def run_single():
    mem_params = mem_params_from_args()
    params_dict = dict()
    params_dict = update_pipeline_params(params_dict)  # update with attributes from user input
    x = RunModel(mem_params,params_dict)
    x.simulator()
    x.report_statistics()


def mem_params_from_args():
    mem_params = MEM_DICT
    if 'dir' in args_params:
        mem_params['mem_path'] = args_params['dir']
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
    print("en_anomaly     True/False             Anomaly column - Enabled")


args_params = dict()

if __name__ == '__main__':

    args_params["single"] = False
    args_params["reg"] = False
    args_params["verbose"] = False
    args_params["csv_output"] = False
    args_params["dir"] = SIMULATION_FILE
    args_params["ptrMax"] = None
    args_params["en_anomaly"] = DEFAULT_EN_ANOMALY

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
        elif arg.startswith("en_anomaly="):
            args_params["en_anomaly"] = int(arg.split("=")[1])

    if args_params["single"]:
        run_single()
    elif args_params["reg"]:
        run_rgr()



