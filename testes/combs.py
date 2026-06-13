import os
import numpy as np

from scripts import readV
from scripts import extData
from scripts import dir
from scripts import Decoder
from scripts import makeCSV
from scripts import lockCombinations

def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

def create_csv(coluns_to_make: str, csv_dir, csv_path):
    table = makeCSV.Create_table(coluns_to_make, csv_dir, csv_path)
    table.make_csv()  

def insert_csv(csv_path, data):
    row = makeCSV.Edit_csv(csv_path, data)
    row.insert_csv_data()

def mean(values: list) -> float:
    return np.mean(values)


colunns_list = [
    'COMBINATION',
    'ARRIVAL',
    'POWER'
    
]



circuit = "c17"

dir_out = f"./output/transitions/{circuit}"

csv_name = f"t_{circuit}"
dir_csv = "./output/base_line/tables"
csv_path = os.path.join(dir_csv, f'{csv_name}.csv') 
base_verilog_path = './data/verilogs_base'

# Registro dos gates ja dimensionados
already_sized = {}

gio = readV.Get_IO(f"0_{circuit}.v", base_verilog_path)
cells_id = gio.get_cells_ids()

TOTAL_GATES = len(cells_id)
alocated_list = [None] * TOTAL_GATES

all_combs = list(lockCombinations.generate_comb(alocated_list, already_sized))

try:
    create_csv(colunns_list, dir_csv, csv_path)
except Exception as error:
    print(error)

for transition in all_combs:

    id_file_sized = decoder_file_name(TOTAL_GATES, transition)

    sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)

    sta_data_sized = extData.Read_timing(sta_sized)

    arrivals_sized = sta_data_sized.get_arrival_times()
    arrivals_values_sized = np.array(list(arrivals_sized.values()))

    mean_arrivals_sized = mean(arrivals_values_sized)

    power = sta_data_sized.get_power()
    #ocurence = sta_data_sized.count_ocurence_path()

    insert_csv(csv_path, [transition, mean_arrivals_sized, power])