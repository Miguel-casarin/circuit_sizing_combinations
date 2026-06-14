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

circuit = "c17"
MAX_WORKERS = 6

colunns_list = [
    'COMBINATION',
    'CHOSEN',
    'SIZED GATE',
    'COST AREA',
    'ARRIVAL',
    'POWER'
]

SIZE_ORDER = ["X1", "X2", "X4", "X8", "X16", "X32"]

# diretórios
json_file = "./data/area_json/areas_nangate.json"

circuit_to_start = f'./data/verilogs_base/{circuit}.v'
base_verilog_path = "./data/verilogs_base"

tcl_file = "tcl_scripts/t.tcl"

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

# Roda as combinações subsequentes
sta_worker = worker.Worker_combinations(
    circuit=circuit,
    circuit_to_start=circuit_to_start,
    temp_dir=temp,
    base_tcl=tcl_file,
    drives=drives,
    json_file=json_file,
    TOTAL_GATES=TOTAL_GATES,
    curente_stage=curente_stage
)

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

    if not current_values:
        log("Nenhum valor coletado. Encerrando.")
        break

    current_lower       = min(current_values)
    best                = min(rows_buffer, key=lambda r: r["mean_arrivals_sized"])
    current_combination = eval(best["comb"])

    if current_lower > previos_lower:
        for row in rows_buffer:
            row_data = [row["comb"], 0, row["dim_gate"], row["area_cost"], row["mean_arrivals_sized"], row["power"]]
            makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()

        log(f"FIM — arrival {current_lower} maior que {previos_lower}")
        break

    else:
        for row in rows_buffer:
            chosen   = 1 if row["comb"] == str(current_combination) else 0
            row_data = [row["comb"], chosen, row["dim_gate"], row["area_cost"], row["mean_arrivals_sized"], row["power"]]
            makeCSV.Edit_csv(csv_path, row_data).insert_csv_data()

        log(f"Transição escolhida → {current_combination} | delay={current_lower}")

        # atualiza o worker para a próxima rodada
        sta_worker.update_stage(current_combination)

        previos_lower       = current_lower
        current_transitions = mt.get_transitions(current_combination, drives, library)
        curente_stage       = current_combination
        count += 1

        keep_verilog = f"{utils.decoder_file_name(TOTAL_GATES, curente_stage)}_{circuit}.v"
        keep_sta = f"{utils.decoder_file_name(TOTAL_GATES, curente_stage)}_{circuit}.txt"

        utils.clear_temp_dir(keep_verilog, keep_sta, temp)

utils.clear_directory(temp)

end_timer = time.time()
log(f"TEMPO TOTAL {(end_timer - start_timer) / 60:.2f} min")
log_file.close()

