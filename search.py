import os 
import numpy as np

from scripts import readV
from scripts import Decoder
from scripts import getFeatures
from scripts import extData
from scripts import singleSTA
from scripts import getNetlist
from scripts import dir
from scripts import setCombination


def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

def is_dir_empty(path):
    return not any(os.scandir(path))

def mean(values: list) -> float:
    return np.mean(values)
    
def base_transitions(number_gates: int) -> list:
    result = []
    
    for i in range(number_gates):
        temp = ["X1"] * number_gates
        temp[-(i + 1)] = "X2"   # começa pelo final
        result.append(temp)

    return result

def transitions(current_combination: list, size_order: list) -> list:
 
    result = []

    for i, element in enumerate(current_combination):
        current_index = size_order.index(element)

        # Só avança se não for o último tamanho
        if current_index < len(size_order) - 1:
            next_size = size_order[current_index + 1]

            new_combination = current_combination.copy()
            new_combination[i] = next_size  # avança só a posição i

            if new_combination not in result:
                result.append(new_combination)

    return result


circuit = "c17"


base_verilog_path = f'./data/verilogs_base'

dir_graph = f'./output/graph/{circuit}'
circuit_to_start = f'./data/verilogs_base/{circuit}.v'

# iformações basicas do netlist
try:
    gio = readV.Get_IO(f"{circuit}.v", base_verilog_path)
    cells_id = gio.get_cells_ids()
    print(cells_id)
except Exception as error:
    print(f"ERROR to get number cells {error}")

TOTAL_GATES = len(cells_id)
SIZE_ORDER = ["X1", "X2", "X4"]
count = 1

# executa o não dimensionado
curente_stage = ["X1"] * TOTAL_GATES
id_file_sized = decoder_file_name(TOTAL_GATES, curente_stage)
name_to_save = f"{id_file_sized}_{circuit}.v"

print(f"{curente_stage} - {name_to_save}")
print(TOTAL_GATES)
if is_dir_empty(dir_graph):
# chama o make verilog individualmente
    try:
        setCombination.apply_combination(circuit_to_start, dir_graph, curente_stage, name_to_save)
    except Exception as error:
        print(f"ERRO to run single {error}")

