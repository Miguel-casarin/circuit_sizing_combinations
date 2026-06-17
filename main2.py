import os
import numpy as np 
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts import readV
from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import makeTransitions
from scripts import getArea
from scripts import makeCSV
from scripts import utils
from scripts import worker
from scripts import getFeatures

circuit = "c17"
MAX_WORKERS = 8
DELET_FILES = True
SAVE_COMBINATION = True

colunns_list = [
    'COMBINATION',
    'SIZE',
    'WEIGHT',
    'CHOSEN',
    'SIZED GATE',
    'PATH_OCURENCE',
    'FA-IN',
    'FA-OUT',
    'LOGIC-LEVEL',
    'DEEP',
    'COST-AREA',
    'ARRIVAL',
    'POWER'
]

if not SAVE_COMBINATION:
    colunns_list.remove('COMBINATION')

SIZE_ORDER = ["X1", "X2", "X4", "X8", "X16", "X32"]

# diretórios
json_file = "./data/area_json/areas_nangate.json"

circuit_to_start = f'./data/verilogs_base/{circuit}.v'
base_verilog_path = "./data/verilogs_base"

tcl_file = "tcl_scripts/t.tcl"

lib = "ed_Nangate.lib"
lib_path = "./data/cells_library"

temp = "./output/temp"

logs_dir = "./output/logs"
log_path = f"{logs_dir}/{circuit}_log.txt"
log_file = open(log_path, "w", encoding="utf-8")

csv_name = f"{circuit}"
dir_csv = "./output/tables"
csv_path = os.path.join(dir_csv, f'{csv_name}.csv')  

with open(json_file) as f:
    library = json.load(f)

# Contabiliza o tempo de execução
start_timer = time.time()

def log(msg):
    print(msg)
    log_file.write(msg + "\n")

try:

    features = getFeatures.Circuits_features(
    f"{circuit}.v",   
    base_verilog_path,
    lib,
    lib_path
)

    dict_fain = features.fan_in()
    dict_faout = features.fan_out()
    dict_logic_level = features.compute_logic_levels()
    dict_deep = features.comput_deep()

    fain_list = utils.dict_to_list(dict_fain)
    faout_list = utils.dict_to_list(dict_faout)
    logic_level_list = utils.dict_to_list(dict_logic_level)
    deep_list = utils.dict_to_list(dict_deep)

    log(f"FA-IN:\n{dict_fain}")
    log(f"{fain_list}")
    log(f"FA-OUT:\n{dict_faout}")
    log(f"{faout_list}")
    log(f"LOGIC-LEVELS:\n{dict_logic_level}")
    log(f"{logic_level_list}")
    log(f"DEEP:\n{dict_deep}")
    log(f"{deep_list}")

except Exception as error:
    print(f"ERROR to get design features {error}")

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

# id das celulas para pesquisar ocorencia nos caminhos
try:
    cells_id = gio.get_cells_ids()
    log(f"Cells ID:\n{cells_id}")
except Exception as error:
    print(f"Error to get cells id {error}")

fa = getArea.Get_Area(json_file)

TOTAL_GATES = len(cells_id)
count = 1

curente_stage = ["X1"] * TOTAL_GATES
id_file_sized = utils.decoder_file_name(TOTAL_GATES, curente_stage)
name_to_save = f"{id_file_sized}_{circuit}.v"

mt = makeTransitions.Make_transitions(SIZE_ORDER)

try:
    sized_weight = utils.combination_weight(curente_stage)
except Exception as error:
    print(f"ERROR to gete weigth {error}")

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
                *([str(curente_stage)] if SAVE_COMBINATION else []),
                1,
                sized_weight,
                1,
                0,   # SIZED GATE
                0,
                0,   # FA-IN
                0,   # FA-OUT
                0,   # LOGIC-LEVEL
                0,   # DEEP
                0.0, # COST-AREA
                previos_lower,  # ARRIVAL
                power           # POWER  <- estava faltando
            ]

    edit = makeCSV.Edit_csv(csv_path, initial_row)
    edit.insert_csv_data()
except Exception as error:
    print(f"ERROR to insert initial state in CSV {error}")

# Pega a ocorencia por caminho crítico usando o base line
dict_ocurence = {}
try:
    base_line = f"0_{circuit}.txt"
    dir_base = f"./output/temp/{base_line}"
    data_path = extData.Read_timing(dir_base)

    dict_ocurence = data_path.count_ocurence_path()
    log(f"PATHS:\n{dict_ocurence}")
except Exception as error:
    print(f"ERROR to get path ocurence {error}")

# Roda as combinações subsequentes
sta_worker = worker.Worker_combinations(
    circuit=circuit,
    circuit_to_start=circuit_to_start,
    temp_dir=temp,
    base_tcl=tcl_file,
    drives=drives,
    json_file=json_file,
    TOTAL_GATES=TOTAL_GATES,
    curente_stage=curente_stage,
    fain_list=fain_list,
    faout_list=faout_list,
    logic_level_list=logic_level_list,
    deep_list=deep_list,
    path_dict=dict_ocurence,
    cells_id=cells_id
)

# guarda o melhor valor das combinações 
best_global = None

while True:
    current_values = []
    rows_buffer = []

    log(f"RODADA {count}")
    log(f"ESTADO ATUAL:\n{curente_stage}\nARRIVAL:\n{previos_lower}\n")

    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        futures = {
            executor.submit(sta_worker.process, comb, i): comb
            for i, comb in enumerate(current_transitions)
        }

        for future in as_completed(futures):
            result = future.result()
            if result:
                rows_buffer.append(result)
                current_values.append(result["mean_arrivals_sized"])
                log(f"{result['comb']} → arrival={result['mean_arrivals_sized']:.5f} power={result['power']}")
                log(f"Combinacao anterior: {result['prev_drives']}")
                log(f"Combinacoes: {result['comb_drives']}")
                log(f"Area anterior: {result['prev_area']} area comb: {result['comb_area']} custo: {result['area_cost']}")
                log(f"Gate dimensionado: {result['dim_gate']}")

    if not current_values:
        log("Nenhum valor coletado. Encerrando.")
        break

    current_lower       = min(current_values)
    best                = min(rows_buffer, key=lambda r: r["mean_arrivals_sized"])
    current_combination = best["comb"]

    if best_global is None or best["mean_arrivals_sized"] < best_global["mean_arrivals_sized"]:
        best_global = best

    if current_lower > previos_lower:
        for row in rows_buffer:
            chosen   = 1 if row["comb"] == current_combination else 0
            row_data = [
                        *([str(row["comb"])] if SAVE_COMBINATION else []),
                        row["size"],
                        row["size_weight"],
                        chosen,
                        row["dim_gate"],
                        row["occurrence"],
                        row["fa_in"],
                        row["fa_out"],
                        row["logic_level"],
                        row["deep"],
                        row["area_cost"],
                        row["mean_arrivals_sized"],
                        row["power"]
                        ]
            makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()

        log(f"FIM — arrival {current_lower} maior que {previos_lower}")
        break

    else:
        for row in rows_buffer:
            chosen = 1 if row["comb"] == current_combination else 0
            row_data = [
                        *([str(row["comb"])] if SAVE_COMBINATION else []),
                        row["size"],
                        row["size_weight"],
                        chosen,
                        row["dim_gate"],
                        row["occurrence"],
                        row["fa_in"],
                        row["fa_out"],
                        row["logic_level"],
                        row["deep"],
                        row["area_cost"],
                        row["mean_arrivals_sized"],
                        row["power"]
                        ]
            makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()

        id_chosen = utils.decoder_file_name(TOTAL_GATES, current_combination)
        log(f"#{'-'*30}#")
        log(f"Transicao escolhida -> {current_combination}")
        log(f"Delay -> {current_lower}")
        log(f"ID -> {id_chosen}")
        log(f"#{'-'*30}#\n")

        # atualiza o worker para a próxima rodada
        sta_worker.update_stage(current_combination)

        previos_lower       = current_lower
        current_transitions = mt.get_transitions(current_combination, drives, library)
        curente_stage       = current_combination
        count += 1

        if DELET_FILES:
            keep_verilog = f"{utils.decoder_file_name(TOTAL_GATES, curente_stage)}_{circuit}.v"
            keep_sta = f"{utils.decoder_file_name(TOTAL_GATES, curente_stage)}_{circuit}.txt"

            utils.clear_temp_dir(keep_verilog, keep_sta, temp)
try:
    utils.update_chosen_csv(csv_path, str(best_global["comb"]), chosen_value=2)
    log(f"Melhor global -> {best_global['comb']} | arrival={best_global['mean_arrivals_sized']:.5f}")   
except Exception as error:
    print(f"ERROR to get best delay {error}")

if DELET_FILES:
    utils.clear_directory(temp)

end_timer = time.time()
log(f"TEMPO TOTAL {(end_timer - start_timer) / 60:.2f} min")
log_file.close()

