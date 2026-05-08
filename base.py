import os 
import numpy as np

from scripts import readV
from scripts import getFeatures
from scripts import extData
from scripts import runSTA
from scripts import getNetlist
from scripts import makeCSV
from scripts import dir
from scripts import getArea

def mean(values: list) -> float:
    return np.mean(values)

def is_dir_empty(path):
    return not any(os.scandir(path))

def create_csv(coluns_to_make: str, csv_dir, csv_path):
    table = makeCSV.Create_table(coluns_to_make, csv_dir, csv_path)
    table.make_csv()  

def area_per_gate(gate: int) -> float:
    cells_syt = getNetlist.get_gates(path_verilog)
    cells_id = gio.get_cells_ids()

    # Evita passar listas e valores errados
    if len(cells_syt) == len(cells_id):
        if gate < len(cells_id):
            for i in range(len(cells_id)): 
                if i == gate:
                    return cells_syt[i]
                
colunns_list = [
    'GATE',
    'SIZE',
    'FA-IN',
    'FA-OUT',
    'NL',
    'DEEP',
    'COST-AREA', 
    'F-PATH',
    'ARRIVAL',    
    'POWER'
]

cell_library_path = "./data/cells_library"
cells_library = "ed_Nangate.lib"

dir_circuits = './data/verilogs_base'
dir_out = "./output/base_line/sta_base"
tcl_file = "tcl_scripts/t.tcl"

json_dir = "./data/area_json"
json_areas = "areas_nangate.json"
path_json_areas = os.path.join(json_dir, json_areas)

DEBUG = True

# Chama o sta caso nenhuma simulação tenha sido feita
if is_dir_empty(dir_out):
    runSTA.run_sta(dir_circuits, dir_out, tcl_file)

files_to_proceces = dir.get_files(dir_circuits)

for design in files_to_proceces:
    circuit = ""
    circuit = design

    csv_name = f"{runSTA.rename(circuit)}.v"
    dir_csv = "./output/base_line/tables"
    csv_path = os.path.join(dir_csv, f'{csv_name}.csv')  

    path_out_STA = os.path.join(dir_out, f"{runSTA.rename(circuit)}.txt")

    path_verilog = os.path.join(dir_circuits, f"{circuit}")

    # Estanciando os modulos 
    try:

        gio = readV.Get_IO(f"{circuit}", dir_circuits)
        data_sta = extData.Read_timing(path_out_STA)
        circuit_features = getFeatures.Circuits_features(f"{circuit}", dir_circuits, cells_library, cell_library_path)

    except Exception as error:
        print(f"ERROR to iport modules {error}")

    try:
        cells = gio.get_cells_ids()

    except Exception as error:
        print(f"Error to get netlist cells {error}")   

    size = 1

    try:
        fa_in = circuit_features.fan_in()
        fa_out = circuit_features.fan_out()
        logic_level = circuit_features.compute_logic_levels()
        deep = circuit_features.comput_deep()

    except Exception as error:
        print(f"ERROR to get features {error}")

    try:
        paths_freq = data_sta.count_ocurence_path()
        power = data_sta.get_power()

        arrivals = data_sta.get_arrival_times()
        arrivals_values = np.array(list(arrivals.values()))
        mean_arrivals = mean(arrivals_values)

    except Exception as error:
        print(f"ERROR to process STA data: {error}")

    # coluna cost-area, aqui não vai ter diferença pq e tudo base line
    try:
        maps = []
        cells = gio.get_cells_ids()
        for i in range(len(cells)):
            map = area_per_gate(i)
            
            maps.append(map)

        areas = []
        for j in maps:
            area = getArea.search_area(j, path_json_areas)
            areas.append(area)

    except Exception as error:
        print(f"ERROR to get areas {error}")
    
    if DEBUG:
        print(f"Circuito -> {circuit}")
        print(f"Circuit cells ID -> {cells}")
        print(f"Features:\nFA-IN -> {fa_in}\nFA-OUT -> {fa_out}\nLN -> {logic_level}\nDEEP -> {deep}")
        print(f"Global Circuit:\nOUT PATH FREQ -> {paths_freq}\nPOWER -> {power}\nMEAN ARRIVALS -> {mean_arrivals}")
        print(f"GATES_MAP -> {maps}")
        print(f"AREA -> {areas}")

    try:
        create_csv(colunns_list, dir_csv, csv_path)
    except Exception as error:
        print(error)

    # Preencher o CSV com os dados
    try:
        for i, cell_id in enumerate(cells):
            gate = cell_id  # Usar o ID da célula, não o nome da gate
            size_val = size
            # Adicionar underscores para corresponder às chaves dos dicionários
            cell_key = f"_{cell_id}_"
            fa_in_val = fa_in.get(cell_key, "")
            fa_out_val = fa_out.get(cell_key, "")
            nl_val = logic_level.get(cell_key, "")
            deep_val = deep.get(cell_key, "")
            cost_area = areas[i] if i < len(areas) else ""
            f_path = paths_freq.get(int(cell_id), 0) if paths_freq else 0  # Retorna 0 se não encontrar
            arrival = mean_arrivals
            power_val = power
            
            data = [gate, size_val, fa_in_val, fa_out_val, nl_val, deep_val, cost_area, f_path, arrival, power_val]
            
            edit_csv = makeCSV.Edit_csv(csv_path, data)
            edit_csv.insert_csv_data()
            
    except Exception as error:
        print(f"ERROR to fill CSV: {error}")
