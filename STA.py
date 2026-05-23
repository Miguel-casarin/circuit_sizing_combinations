from scripts import runSTA

import os

def is_dir_empty(path):
    return not any(os.scandir(path))

dir_to_save = "./output/transitions/c3"
verilogs_inputs = "./inputs"
tcl_file = "tcl_scripts/t.tcl"

if is_dir_empty(dir_to_save):
    runSTA.run_sta(verilogs_inputs, dir_to_save, tcl_file)