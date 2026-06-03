import os
import numpy as np 
import json
import time

from scripts import readV
from scripts import Decoder
from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import makeTransitions

def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates range dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base5_to_decimal()

def is_dir_empty(path):
    return not any(os.scandir(path))

def mean(values: list) -> float:
    return np.mean(values)

start_timer = time.time()

json_file = "./data/area_json/areas_nangate.json"

SIZE_ORDER = ["X1", "X2", "X4", "X8", "X16"]

with open(json_file) as f:
    library = json.load(f)

circuit = "teste2"
circuit_to_start = f'./data/verilogs_base/{circuit}.v'
base_verilog_path = "./data/verilogs_base"

tcl_file = "tcl_scripts/t.tcl"

# diretorio temporario, os arquivos serao apagados depois
temp = "./output/temp"

# Escreve as saidas
log_path = f"./{circuit}_log.txt"
log_file = open(log_path, "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")

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

# cria o verilog e roda STA para o estado inicial
try:
    setCombination.apply_combination(circuit_to_start, temp, curente_stage, name_to_save)
except Exception as error:
    print(f"ERROR to make single verilog {error}")

try:
    singleSTA.run_single(tcl_file, name_to_save, temp, temp)
except Exception as error:
    print(f"ERROR to make single STA {error}")

# pega os dados do estado inicial
try:
    sta_start = dir.search_file(f"{id_file_sized}_{circuit}.txt", temp)
    sta_data_sized = extData.Read_timing(sta_start)

    arrivals_start = sta_data_sized.get_arrival_times()
    arrivals_start_sized = np.array(list(arrivals_start.values()))
    previos_lower = mean(arrivals_start_sized)

    power = sta_data_sized.get_power()
    log(f"Power: {power}")
    
except Exception as error:
    print(f"ERROR to read sta files {error}")

log(f"Total de gates: {TOTAL_GATES}")

# roda as combinacoes subsequentes
while True:
    current_values = []

    log(f"RODADA {count}\n")
    log(f"ESTADO ATUAL........-........ARRIVAL\n{curente_stage}........-........{previos_lower}\n")
    log("Combinacoes possíveis")

    for comb in current_transitions:
        id_file_sized = decoder_file_name(TOTAL_GATES, comb)
        name_to_save = f"{id_file_sized}_{circuit}.v"

        try:
            setCombination.apply_combination(circuit_to_start, temp, comb, name_to_save)
        except Exception as error:
            print(f"ERROR to make single verilog {error}")

        try:
            singleSTA.run_single(tcl_file, name_to_save, temp, temp)
        except Exception as error:
            print(f"ERROR to make single STA {error}")

        # lê e processa o resultado do STA
        try:
            sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", temp)
            sta_data_sized = extData.Read_timing(sta_sized)

            arrivals_sized = sta_data_sized.get_arrival_times()
            arrivals_values_sized = np.array(list(arrivals_sized.values()))
            mean_arrivals_sized = mean(arrivals_values_sized)

            power = sta_data_sized.get_power()
            
            log(f"{comb}...........-...........{mean_arrivals_sized}\nPower: {power}")
            current_values.append(mean_arrivals_sized)
        except Exception as error:
            print(f"ERROR to read sta files for {comb}: {error}")

    if not current_values:
        print("Nenhum valor coletado. Encerrando.")
        break

    current_lower = min(current_values)
    current_combination = current_transitions[current_values.index(current_lower)]

    if current_lower > previos_lower or not current_transitions:

        log("FIM\n")
        log(f"Current Lower {current_lower} maior que o anterior {previos_lower}")

        break

    else:

        log(f"#{'-'*30}#")
        id_chosen = decoder_file_name(TOTAL_GATES, current_combination)
        log(f"Transicao escolhida -> {current_combination}\nDelay -> {current_lower}\nID -> {id_chosen}")
        log(f"#{'-'*30}#\n")

        previos_lower = current_lower
        current_transitions = mt.get_transitions(current_combination, drives, library)
        curente_stage = current_combination
        count += 1
end_timer = time.time()
total_time = (end_timer - start_timer) / 60
log(f"TEMPO TOTAL {total_time}")
log_file.close()