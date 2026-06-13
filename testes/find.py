import os
import numpy as np

from scripts import readV
from scripts import extData
from scripts import dir
from scripts import Decoder

def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

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

base_verilog_path = './data/verilogs_base'

circuit = "c3"
dir_out = f"./output/transitions/{circuit}"

gio = readV.Get_IO(f"0_{circuit}.v", base_verilog_path)
cells_id = gio.get_cells_ids()

TOTAL_GATES = len(cells_id)
SIZE_ORDER = ["X1", "X2", "X4"]
count = 1

# Inicializa com as transições base ANTES do while
current_transitions = base_transitions(TOTAL_GATES)
print(f"###### {current_transitions}")
curente_stage = ["X1"] * TOTAL_GATES

id_file_sized = decoder_file_name(TOTAL_GATES, curente_stage)

sta_start = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)
sta_data_sized = extData.Read_timing(sta_start)

arrivals_start = sta_data_sized.get_arrival_times()
arrivals_start_sized = np.array(list(arrivals_start.values()))
start_arrival = mean(arrivals_start_sized)

previos_lower = start_arrival


while True:
    current_values = []

    print(f"RODADA {count}\n")
    print(f"ESTADO ATUAL........-........ARRIVAL\n{curente_stage}........-........{previos_lower}\n")
    print("Combinacoes possíveis")
    for comb in current_transitions:
    
        id_file_sized = decoder_file_name(TOTAL_GATES, comb)
        sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)
        sta_data_sized = extData.Read_timing(sta_sized)

        arrivals_sized = sta_data_sized.get_arrival_times()
        arrivals_values_sized = np.array(list(arrivals_sized.values()))
        mean_arrivals_sized = mean(arrivals_values_sized)

        print(f"{comb}...........-...........{mean_arrivals_sized}")
        current_values.append(mean_arrivals_sized)

    current_lower = min(current_values)
    current_combination = current_transitions[current_values.index(current_lower)]

   

    if current_lower > previos_lower or all(value == "X4" for value in current_combination):
        print("FIM\n")
        print(f"Current Lower {current_lower} maior que o anterior {previos_lower}")
        
        break

    else:
        print(f"#{'-'*30}#")
        print(f"Transicao escolhida -> {current_combination}\nDelay -> {current_lower}")
        print(f"#{'-'*30}#\n")

        previos_lower = current_lower
        # Expande o grafo a partir da melhor combinação
        current_transitions = transitions(current_combination, SIZE_ORDER)
        curente_stage = current_combination
        count += 1