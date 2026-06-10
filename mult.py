import os
import numpy as np 
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from scripts import readV
from scripts import utils
from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import makeTransitions
from scripts import getArea
from scripts import makeCSV
from scripts import processCombinations


colunns_list = [
    'COMBINATION',
    'CHOSEN',
    'SIZED GATE',
    'COST AREA',
    'ARRIVAL',
    'POWER'
]

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
dir_csv = "./output/base_line/tables"
csv_path = os.path.join(dir_csv, f'{csv_name}.csv')  

# Escreve as saidas
log_path = f"./{circuit}_log.txt"
log_file = open(log_path, "w", encoding="utf-8")

def log(msg):
    print(msg)
    log_file.write(msg + "\n")


if __name__ == '__main__':

    start_timer = time.time()

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
        log(f"RODADA {count}\n")
        log(f"ESTADO ATUAL:\n{curente_stage}\nARRIVAL:\n{previos_lower}\n")

        args_list = [
            (comb, circuit_to_start, temp, tcl_file, circuit, TOTAL_GATES)
            for comb in current_transitions
        ]

        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(processCombinations.verilog_and_sta, *args) for args in args_list]
            sta_results = [f.result() for f in as_completed(futures)]
            sta_results = [r for r in sta_results if r is not None]

        rows_buffer = []
        current_values = []

        for sta_result in sta_results:
            result = processCombinations.read_sta_results(sta_result, circuit, drives, json_file, curente_stage)
            if result:
                rows_buffer.append(result)
                current_values.append(result['mean_arrivals_sized'])
                log(f"{result['comb']}...{result['mean_arrivals_sized']}\nPower: {result['power']}")

        if not current_values:
            print("Nenhum valor coletado. Encerrando.")
            break

        current_lower = min(current_values)
        current_combination = current_transitions[current_values.index(current_lower)]

        if current_lower > previos_lower or not current_transitions:
            for row in rows_buffer:
                try:
                    row_data = [row['comb'], 0, row['dim_gate'], row['area_cost'], row['mean_arrivals_sized'], row['power']]
                    makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()
                except Exception as e:
                    print(f"ERROR to insert CSV data {e}")

            log("FIM\n")
            log(f"Current Lower {current_lower} maior que o anterior {previos_lower}")
            break

        else:
            log(f"#{'-'*30}#")
            id_chosen = utils.decoder_file_name(TOTAL_GATES, current_combination)
            log(f"Transicao escolhida -> {current_combination}\nDelay -> {current_lower}\nID -> {id_chosen}")
            log(f"#{'-'*30}#\n")

            for row in rows_buffer:
                try:
                    chosen = 1 if row['comb'] == str(current_combination) else 0
                    row_data = [row['comb'], chosen, row['dim_gate'], row['area_cost'], row['mean_arrivals_sized'], row['power']]
                    makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()
                except Exception as e:
                    print(f"ERROR to insert CSV data {e}")

            previos_lower = current_lower
            current_transitions = mt.get_transitions(current_combination, drives, library)
            curente_stage = current_combination
            count += 1

    end_timer = time.time()
    print(f"TEMPO TOTAL {(end_timer - start_timer) / 60}")
    log(f"TEMPO TOTAL {(end_timer - start_timer) / 60}")
    log_file.close()