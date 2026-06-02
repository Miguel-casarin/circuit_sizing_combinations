import os
import numpy as np 
import json

from scripts import readV
from scripts import Decoder
from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import makeTransitions

def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

def is_dir_empty(path):
    return not any(os.scandir(path))

def mean(values: list) -> float:
    return np.mean(values)

json_file = "./data/area_json/areas_nangate.json"

SIZE_ORDER = ["X1", "X2", "X4", "X8", "X16"]

with open(json_file) as f:
    library = json.load(f)

circuit = "c3"
circuit_to_start = f'./data/verilogs_base/{circuit}.v'
base_verilog_path = "./data/verilogs_base"

tcl_file = "tcl_scripts/t.tcl"

# diretorio temporario os arquivos seram apagados depois 
temp = "./output/temp"

try:
    cells_drives = readV.Find_Drive_cells(f"{circuit}.v", base_verilog_path)
    drives = cells_drives.parse_drives()
except Exception as error:
    print(f"ERROR to find drive cells {error}")

try:
    gio = readV.Get_IO(f"{circuit}.v", base_verilog_path)
    cells_id = gio.get_cells_ids()
    print(cells_id)
except Exception as error:
    print(f"ERROR to get number cells {error}")

TOTAL_GATES = len(cells_id)
count = 1

curente_stage = ["X1"] * TOTAL_GATES
id_file_sized = decoder_file_name(TOTAL_GATES, curente_stage)
name_to_save = f"{id_file_sized}_{circuit}.v"

mt = makeTransitions.Make_transitions(SIZE_ORDER)

try:
    current_transitions = mt.get_base_transitions(TOTAL_GATES, drives, library)
except Exception as error:
    print(f"ERROR to set base transitions {error}")

# cria os arquivos
try:
    setCombination.apply_combination(circuit_to_start, temp, curente_stage, name_to_save)
except Exception as error:
    print(f"ERROR to make single verilog {error}")

try:
    singleSTA.run_single(tcl_file, name_to_save, temp, temp)
except Exception as error:
    print(f"ERROR to make single STA {error}")

# pega os dados base
try:

    sta_start = dir.search_file(f"{id_file_sized}_{circuit}.txt", temp)
    sta_data_sized = extData.Read_timing(sta_start)

    arrivals_start = sta_data_sized.get_arrival_times()
    arrivals_start_sized = np.array(list(arrivals_start.values()))
    start_arrival = mean(arrivals_start_sized)

    previos_lower = start_arrival
    
except Exception as error:
    print(f"ERROR to read sta files {error}")

# Roda as combinações subsequentes
while True:
    current_values = []

    for comb in current_transitions:
        id_file_sized = decoder_file_name(TOTAL_GATES, comb)
        name_to_save = f"{id_file_sized}_{circuit}.v"

    # cria os arquivos
    try:
        setCombination.apply_combination(circuit_to_start, temp, curente_stage, name_to_save)
    except Exception as error:
        print(f"ERROR to make single verilog {error}")

    try:
        singleSTA.run_single(tcl_file, name_to_save, temp, temp)
    except Exception as error:
        print(f"ERROR to make single STA {error}")

    # pega os dados base
    try:

        sta_start = dir.search_file(f"{id_file_sized}_{circuit}.txt", temp)
        sta_data_sized = extData.Read_timing(sta_start)

        arrivals_start = sta_data_sized.get_arrival_times()
        arrivals_start_sized = np.array(list(arrivals_start.values()))
        start_arrival = mean(arrivals_start_sized)

        previos_lower = start_arrival
        
    except Exception as error:
        print(f"ERROR to read sta files {error}") 

    current_lower = min(current_values)
    current_combination = current_transitions[current_values.index(current_lower)]

    if current_lower > previos_lower or not current_transitions:
        break

    else:
        id_chosen = decoder_file_name(TOTAL_GATES, current_combination)
        

        previos_lower = current_lower
        current_transitions = mt.base_transitions(current_combination, drives, library)
        curente_stage = current_combination
        count += 1