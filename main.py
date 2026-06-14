import os
import numpy as np 
import json
import time

from scripts import readV
from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import makeTransitions
from scripts import getArea
from scripts import makeCSV
from scripts import utils





colunns_list = [
    'COMBINATION',
    'CHOSEN',
    'SIZED GATE',
    'COST AREA',
    'ARRIVAL',
    'POWER'
]

start_timer = time.time()

json_file = "./data/area_json/areas_nangate.json"

SIZE_ORDER = ["X1", "X2", "X4", "X8", "X16", "X32"]

with open(json_file) as f:
    library = json.load(f)

circuit = "c17"
circuit_to_start = f'./data/verilogs_base/{circuit}.v'
base_verilog_path = "./data/verilogs_base"

tcl_file = "tcl_scripts/t.tcl"

# diretorio temporario, os arquivos serao apagados depois
temp = "./output/temp"

# diretorios dos csvs
csv_name = f"{circuit}"
dir_csv = "./output/tables"
csv_path = os.path.join(dir_csv, f'{csv_name}.csv')  

# Escreve as saidas
logs_dir = "./output/logs"
log_path = f".{logs_dir}/{circuit}_log.txt"
log_file = open(log_path, "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")

try:
    cells_drives = readV.Find_Drive_cells(f"{circuit}.v", base_verilog_path)
    drives = cells_drives.parse_drives()
    print(f"---------> {drives}")
except Exception as error:
    print(f"ERROR to find drive cells {error}")

try:
    gio = readV.Get_IO(f"{circuit}.v", base_verilog_path)
    cells_id = gio.get_cells_ids()
    print(cells_id)
except Exception as error:
    print(f"ERROR to get number cells {error}")

fa = getArea.Get_Area(json_file)

TOTAL_GATES = len(cells_id)
count = 1

curente_stage = ["X1"] * TOTAL_GATES
id_file_sized = utils.decoder_file_name(TOTAL_GATES, curente_stage)
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
    previos_lower = utils.mean(arrivals_start_sized)

    power = sta_data_sized.get_power()
    log(f"Power: {power}")
    
except Exception as error:
    print(f"ERROR to read sta files {error}")

log(f"Total de gates: {TOTAL_GATES}")

try:
    utils.create_csv(colunns_list, dir_csv, csv_path)
except Exception as error:
    print(f"ERRPR to make CSV {error}")

# Insere o estado inicial no CSV
try:
    initial_comb = utils.merge_size_id(drives, curente_stage)
    initial_area = fa.return_total_area(initial_comb)

    initial_row = [
        str(curente_stage),
        1,  
        0,                   # SIZED GATE (estado inicial, nenhum gate dimensionado)
        0.0,                 # COST AREA (referência, custo zero)
        previos_lower,       # ARRIVAL
        power               # POWER                         
    ]

    edit = makeCSV.Edit_csv(csv_path, initial_row)
    edit.insert_csv_data()
except Exception as error:
    print(f"ERROR to insert initial state in CSV {error}")

# roda as combinacoes subsequentes
while True:
    current_values = []
    rows_buffer = []  # guarda os dados de cada combinacao antes de inserir no CSV

    log(f"RODADA {count}\n")
    log(f"ESTADO ATUAL:\n{curente_stage}\nARRIVAL:\n{previos_lower}\n")
    log("Combinacoes possíveis")

    for comb in current_transitions:
        id_file_sized = utils.decoder_file_name(TOTAL_GATES, comb)
        name_to_save = f"{id_file_sized}_{circuit}.v"

        mean_arrivals_sized = None
        power = None
        area_cost = None
        dim_gate = None

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
            mean_arrivals_sized = utils.mean(arrivals_values_sized)

            power = sta_data_sized.get_power()
            
            log(f"{comb}...........-...........{mean_arrivals_sized}\nPower: {power}")
            current_values.append(mean_arrivals_sized)
        except Exception as error:
            print(f"ERROR to read sta files for {comb}: {error}")

        # calcula a direfença da area
        try:
            previos_comb = utils.merge_size_id(drives, curente_stage)
            previos_area = fa.return_total_area(previos_comb)

            comb_drives = utils.merge_size_id(drives, comb)
            comb_area = fa.return_total_area(comb_drives)

            area_cost = fa.cost(comb_area, previos_area)
            dim_gate = utils.find_changed_index(curente_stage, comb)
            log(f"Combinacao anterior {previos_comb}")
            log(f"combinacoes {comb_drives}")
            log(f"area anterior {previos_area} area comb {comb_area} custo {area_cost}")
            log(f"gate dimensionado {dim_gate}")
        except Exception as error:
            print(f"ERROR to get area {error}")

        # guarda os dados da combinacao no buffer para inserir depois com CHOSEN correto
        if all(v is not None for v in [mean_arrivals_sized, power, area_cost, dim_gate]):
            rows_buffer.append({
                'comb': str(comb),
                'dim_gate': int(dim_gate),
                'area_cost': area_cost,
                'mean_arrivals_sized': mean_arrivals_sized,
                'power': power
            })

    if not current_values:
        print("Nenhum valor coletado. Encerrando.")
        break

    current_lower = min(current_values)
    current_combination = current_transitions[current_values.index(current_lower)]

    if current_lower > previos_lower or not current_transitions:

        # nenhuma combinacao foi escolhida, insere todas com CHOSEN=0
        for row in rows_buffer:
            try:
                row_data = [
                    row['comb'],
                    0,
                    row['dim_gate'],
                    row['area_cost'],
                    row['mean_arrivals_sized'],
                    row['power']
                    
                ]
                edit = makeCSV.Edit_csv(csv_path, row_data)
                edit.insert_csv_data()
            except Exception as error:
                print(f"ERROR to insert CSV data {error}")

        log("FIM\n")
        log(f"Current Lower {current_lower} maior que o anterior {previos_lower}")

        break

    else:

        log(f"#{'-'*30}#")
        id_chosen = utils.decoder_file_name(TOTAL_GATES, current_combination)
        log(f"Transicao escolhida -> {current_combination}\nDelay -> {current_lower}\nID -> {id_chosen}")
        log(f"#{'-'*30}#\n")

        # insere todas as combinacoes com CHOSEN=1 apenas para a escolhida
        for row in rows_buffer:
            try:
                chosen = 1 if row['comb'] == str(current_combination) else 0
                row_data = [
                    row['comb'],
                    chosen,
                    row['dim_gate'],
                    row['area_cost'],
                    row['mean_arrivals_sized'],
                    row['power']
                ]
                edit = makeCSV.Edit_csv(csv_path, row_data)
                edit.insert_csv_data()
            except Exception as error:
                print(f"ERROR to insert CSV data {error}")

        previos_lower = current_lower
        current_transitions = mt.get_transitions(current_combination, drives, library)
        curente_stage = current_combination
        count += 1

end_timer = time.time()
total_time = (end_timer - start_timer) / 60
log(f"TEMPO TOTAL {total_time}")
log_file.close()