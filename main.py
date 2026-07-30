import os
import numpy as np 
import json
import time
import traceback
import sys
import json
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
from scripts import errors
from scripts import dict

circuit = "b01_C"
MAX_WORKERS = max(1, os.cpu_count() - 1)
DELET_FILES = True
SAVE_COMBINATION = False

colunns_list = [
    'COMBINATION',
    'SIZED-GATE',
    'SIZE',
    'LOGIC-TYPE',
    'CELL-AREA',
    'WEIGHT',
    'CHOSEN',
    'PATH-OCURENCE',
    'PATHS-OCURENCE',
    'FA-IN',
    'FA-OUT',
    'LOGIC-LEVEL',
    'DEEP',
    'COST-AREA',
    'ARRIVAL',
    'ARRIVAL-DIFF',
    'POWER'
]

if not SAVE_COMBINATION:
    colunns_list.remove('COMBINATION')

SIZE_ORDER = ["X1", "X2"]

# diretórios
json_file = "./data/area_json/areas.json"

circuit_to_start = f'./data/verilogs_base/{circuit}.v'
base_verilog_path = "./data/verilogs_base"

tcl_file = "tcl_scripts/t.tcl"

dict_joson = f"{circuit}_features.json"

lib = "Nangate45_typ.lib"
lib_path = "./data/cells_library"

temp = "./output/temp"

debug_dir = "./output/logs_debug"
debug_path = f"{debug_dir}/{circuit}_log.txt"
debug_file = open(debug_path, "w", encoding="utf-8")

log_error_dir = "./output/logs_error"
log_error_path = f"{log_error_dir}/{circuit}.log"
error_file = open(log_error_path, "w", encoding="utf-8")

csv_name = f"{circuit}"
dir_csv = "./output/tables"
csv_path = os.path.join(dir_csv, f'{csv_name}.csv')  

with open(json_file) as f:
    library = json.load(f)

# Contabiliza o tempo de execução
start_timer = time.time()

def log_debug(msg: str):
    debug_file.write(msg + "\n")

def log_error(msg: str):
    error_file.write(msg + "\n")

try:
    design = readV.Get_IO(f"{circuit}.v", base_verilog_path)
    design_module = design.verilog_module()
    design_inputs = design.get_inputs()
    design_outputs = design.get_outputs()
except Exception as error:
    print(f"ERROR read verilog {error}")
    errors.fatal("ERROR to read verilog", error, debug_file, error_file)

try:
    gio = readV.Gates_info(f"{circuit}.v", base_verilog_path)
except Exception as error:
    print(f"ERROR read verilog {error}")
    errors.fatal("ERROR to read verilog", error, debug_file, error_file)

# id das celulas para pesquisar ocorencia nos caminhos
try:
    cells_id = gio.get_cells_ids()
    log_debug(f"Cells ID:\n{cells_id}")
except Exception as error:
    print(f"Error to get cells id {error}")
    errors.fatal("ERROR to get celols ID", error, debug_file, error_file)

try:
    cells_logic_types_netlist = readV.Gates_info(f"{circuit}.v", base_verilog_path)

    logic_types_netlist = cells_logic_types_netlist.lugic_cells_type()
    print(logic_types_netlist)
except Exception as error:
    print(f"ERROR to find drive cells {error}")
    errors.fatal("ERROR to find drive cells", error, debug_file, error_file)

try:
    features_dict = dict.Manipulet_dict()
    features_dict.fild_dictionary(cells_id, logic_types_netlist)
except Exception as error:
    print(f"ERROR to load dict {error}")
    errors.fatal("ERROR to fild dict", error, debug_file, error_file)
    debug_file.flush()
    error_file.flush()
    debug_file.close()
    error_file.close()
    sys.exit(1)

if len(features_dict.nets_and_path) == 0:
    print(f"Unfilled dictionary")
    errors.fatal("dictionary keys not load", error, debug_file, error_file)
    debug_file.flush()
    error_file.flush()
    debug_file.close()
    error_file.close()
    sys.exit(1)

else:
    try:
        extactor_features = getFeatures.Circuits_features(f"{circuit}.v", base_verilog_path, lib, lib_path, features_dict)

        extactor_features.compute_logic_levels()
        extactor_features.comput_deep()
        extactor_features.fan_in()
        extactor_features.fan_out()
        extactor_features.loaded_cells()

    except Exception as error:
        print(f"ERROR to load circuit features to dict")
        errors.fatal("ERROR to load netlist features to dict", error, debug_file, error_file)






features_dict_keys = list(features_dict.nets_and_path)

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
    errors.fatal("ERROR to gate weigth", error, debug_file, error_file)

try:
    current_transitions = mt.get_base_transitions(TOTAL_GATES, logic_types_netlist, library)
except Exception as error:
    print(f"ERROR to set base transitions {error}")
    errors.fatal("ERROR to set base transitions", error, debug_file, error_file)

# cria o verilog e roda STA para o estado inicial
try:
    setCombination.apply_combination(circuit_to_start, temp, curente_stage, name_to_save)
except Exception as error:
    print(f"ERROR to make single verilog {error}")
    errors.fatal("ERROR to make single verilog", error, debug_file, error_file)

try:
    singleSTA.run_single(tcl_file, name_to_save, temp, temp, design_module, design_inputs, design_outputs )
except Exception as error:
    print(f"ERROR to make single STA {error}")
    errors.fatal("ERROR to make single STA", error, debug_file, error_file)

# pega os dados do estado inicial
try:
    sta_start = dir.search_file(f"{id_file_sized}_{circuit}.txt", temp)
    sta_data_sized = extData.Read_timing(sta_start)

    arrivals_start = sta_data_sized.get_arrival_times()
    arrivals_start_sized = np.array(list(arrivals_start.values()))
    previos_lower = utils.mean(arrivals_start_sized)

    power = sta_data_sized.get_power()
    log_debug(f"Power: {power}")
    
except Exception as error:
    print(f"ERROR to read sta files {error}")
    errors.fatal("ERROR to read sta files", error, debug_file, error_file)

# Pega a ocorencia por caminho crítico usando o base line
dict_ocurence = {}
dict_paths = {}

try:
    base_line = f"0_{circuit}.txt"
    dir_base = f"./output/temp/{base_line}"
    data_path = extData.Read_timing(dir_base)

    dict_ocurence = data_path.count_ocurence_path()
    log_debug(f"PATH:\n{dict_ocurence}")

    dict_paths = data_path.ocurence_by_paths()
    log_debug(f"PATHS:\n{dict_paths}")

    # Preenche as ocorrências no dicionário principal
    utils.merge_dicts(features_dict.nets_and_path, "PATH-OCURENCE", dict_ocurence)
    utils.merge_dicts(features_dict.nets_and_path, "PATHS-OCURENCE", dict_paths)

except Exception as error:
    print(f"ERROR to get path ocurence {error}")
    errors.fatal("ERROR to get path ocurence", error, debug_file, error_file)



log_debug(f"Total de gates: {TOTAL_GATES}")

try:
    utils.create_csv(colunns_list, dir_csv, csv_path)
except Exception as error:
    print(f"ERRPR to make CSV {error}")
    errors.fatal("ERRPR to make CSV", error, debug_file, error_file)

currente_arrival = previos_lower
# Insere o estado inicial no CSV
try:
    initial_comb = utils.merge_size_id(logic_types_netlist, curente_stage)
    initial_area = fa.return_total_area(initial_comb)

    initial_row = [
                *([str(curente_stage)] if SAVE_COMBINATION else []),
                0,
                0,
                None,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                previos_lower,  # ARRIVAL
                currente_arrival,
                power           # POWER  <- estava faltando
            ]

    edit = makeCSV.Edit_csv(csv_path, initial_row)
    edit.insert_csv_data()
except Exception as error:
    print(f"ERROR to insert initial state in CSV {error}")
    errors.fatal("ERROR to insert initial state in CSV", error, debug_file, error_file)

# Roda as combinações subsequentes
sta_worker = worker.Worker_combinations(
    circuit=circuit,
    circuit_to_start=circuit_to_start,
    temp_dir=temp,
    design_module= design_module,
    design_inputs= design_inputs,
    design_outputs = design_outputs,
    base_tcl=tcl_file,
    drives=logic_types_netlist,
    json_file=json_file,
    TOTAL_GATES=TOTAL_GATES,
    curente_stage=curente_stage,
    logic_types=logic_types_netlist,
    features_dict=features_dict.nets_and_path
)

# guarda o melhor valor das combinações 
best_global = None
best_global_row_index = None
csv_row_counter = 2 # começo em 2 para pular o cebeçalho e o baseline



while True:
    current_values = []
    rows_buffer = []

    log_debug(f"RODADA {count}")
    log_debug(f"ESTADO ATUAL:\n{curente_stage}\nARRIVAL:\n{previos_lower}\n")

    loop_error = None

    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        futures = {
            executor.submit(sta_worker.process, comb, i): comb
            for i, comb in enumerate(current_transitions)
        }

        try:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    rows_buffer.append(result)
                    current_values.append(result["mean_arrivals_sized"])
                    log_debug(f"{result['comb']} → arrival={result['mean_arrivals_sized']:.5f} power={result['power']}")
                    log_debug(f"Combinacao anterior: {result['prev_drives']}")
                    log_debug(f"Combinacoes: {result['comb_drives']}")
                    log_debug(f"Area anterior: {result['prev_area']} area comb: {result['comb_area']} custo: {result['area_cost']}")
                    log_debug(f"Gate dimensionado: {result['dim_gate']}")

        except Exception as error:
            comb_failed = futures.get(future, "desconhecida")
            loop_error = error

            log_error(f"\n{'#'*60}")
            log_error(f"ERRO FATAL na rodada {count}, combinação {comb_failed}")
            print(f"ERRO FATAL na rodada {count}, combinação {comb_failed}")
            log_error(f"{error}")
            log_error(traceback.format_exc())
            log_error(f"{'#'*60}\n")

            # cancela as tasks que ainda não começaram a rodar
            for f in futures:
                f.cancel()

    if loop_error is not None:
        log_error("Loop principal abortado por erro. Encerrando execução sem continuar para a próxima rodada.")
        debug_file.flush()
        error_file.flush()
        debug_file.close()
        error_file.close()
        sys.exit(1)


    if not current_values:
        log_debug("Nenhum valor coletado. Encerrando.")
        break

    current_lower       = min(current_values)
    best                = min(rows_buffer, key=lambda r: r["mean_arrivals_sized"])
    current_combination = best["comb"]

    currente_arrival = current_lower

    if best_global is None or best["mean_arrivals_sized"] < best_global["mean_arrivals_sized"]:
        best_global = best
        best_global_row_index = csv_row_counter + rows_buffer.index(best)  # ← salva índice

    if current_lower > previos_lower:
        for row in rows_buffer:
            chosen   = 1 if row["comb"] == current_combination else 0

            arrival_diff = previos_lower - row["mean_arrivals_sized"] 

            row_data = [
                        *([str(row["comb"])] if SAVE_COMBINATION else []),
                        row["dim_gate"],
                        row["size"],
                        row["logic_type"],
                        row["cell-area"],
                        row["size_weight"],
                        chosen,
                        row["occurrence"],
                        row["fa_in"],
                        row["fa_out"],
                        row["logic_level"],
                        row["deep"],
                        row["area_cost"],
                        row["mean_arrivals_sized"],
                        arrival_diff,
                        row["power"]
                        ]
            makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()

        log_debug(f"FIM — arrival {current_lower} maior que {previos_lower}")
        break


    else:
        for row in rows_buffer:
            chosen = 1 if row["comb"] == current_combination else 0

            arrival_diff = previos_lower - row["mean_arrivals_sized"] 

            row_data = [
                        *([str(row["comb"])] if SAVE_COMBINATION else []),
                        row["dim_gate"],
                        row["size"],
                        row["logic_type"],
                        row["cell-area"],
                        row["size_weight"],
                        chosen,
                        row["occurrence"],
                        row["fa_in"],
                        row["fa_out"],
                        row["logic_level"],
                        row["deep"],
                        row["area_cost"],
                        row["mean_arrivals_sized"],
                        arrival_diff,
                        row["power"]
                        ]
            makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()

        id_chosen = utils.decoder_file_name(TOTAL_GATES, current_combination)
        log_debug(f"#{'-'*30}#")
        log_debug(f"Transicao escolhida -> {current_combination}")
        log_debug(f"Delay -> {current_lower}")
        log_debug(f"ID -> {id_chosen}")
        log_debug(f"#{'-'*30}#\n")

        # atualiza o worker para a próxima rodada
        sta_worker.update_stage(current_combination)

        previos_lower       = current_lower
        current_transitions = mt.get_transitions(current_combination, logic_types_netlist, library)
        curente_stage       = current_combination
        count += 1
        csv_row_counter += len(rows_buffer)

        if DELET_FILES:
            keep_verilog = f"{utils.decoder_file_name(TOTAL_GATES, curente_stage)}_{circuit}.v"
            keep_sta = f"{utils.decoder_file_name(TOTAL_GATES, curente_stage)}_{circuit}.txt"

            utils.clear_temp_dir(keep_verilog, keep_sta, temp)
try:
    utils.update_chosen_by_index(csv_path, best_global_row_index, chosen_value=2)
    log_debug(f"Melhor global -> {best_global['comb']} | arrival={best_global['mean_arrivals_sized']:.5f}")   
except Exception as error:
    print(f"ERROR to get best delay {error}")
    log_error(f"ERROR to get best delay {error}")

if DELET_FILES:
    utils.clear_directory(temp)

try:
    json_path = os.path.join(debug_dir, dict_joson)
    with open(json_path, 'w') as f:
        json.dump(features_dict.nets_and_path, f, indent=4)
    log_debug(f"Dicionário de features salvo em {json_path}")
except Exception as error:
    print(f"ERROR to save JSON {error}")
    log_error(f"ERROR to save JSON {error}")

end_timer = time.time()
log_debug(f"TEMPO TOTAL {(end_timer - start_timer) / 60:.2f} min")
log_error(f"TEMPO TOTAL {(end_timer - start_timer) / 60:.2f} min")
debug_file.close()
error_file.close()


