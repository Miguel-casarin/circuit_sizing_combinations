import os
import numpy as np
import shutil
import time

from scripts import readV
from scripts import getFeatures
from scripts import extData
from scripts import runSTA
from scripts import getNetlist
from scripts import makeCSV
from scripts import dir
from scripts import getArea
from scripts import Decoder
from scripts import lockCombinations
from scripts import edSizeList
from scripts import ReadCSV


# retorna o id do arquivo dado a transição   
def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

SIZE_ORDER = ["X2", "X4"]

def next_size(current):
    if current not in SIZE_ORDER:
        return "X2"
    idx = SIZE_ORDER.index(current)
    if idx + 1 < len(SIZE_ORDER):
        return SIZE_ORDER[idx + 1]
    return None


# carrega a base de dados
circuit = "c3"
input_table = f"data_{circuit}.csv"
data_base = f"./output/base_line/tables/{input_table}"

edited_table_name = f"edit_{input_table}"
output_hank = f"./output/rank/{edited_table_name}"

# verifica se já existe
if not os.path.exists(output_hank):
    shutil.copy(data_base, output_hank)
else:
    print("Arquivo já existe")

dir_out = "./output/transitions/c3"

# Registro dos gates ja dimensionados
already_sized = {}

TOTAL_GATES = 3
alocated_list = [None] * TOTAL_GATES
v = 0



while True:

    indice_lower_delay = ReadCSV.seach_lower(output_hank, "MEAN ARRIVAL")
    print(f"indice -> {indice_lower_delay}")

    lower_delay = ReadCSV.return_value(output_hank, "MEAN ARRIVAL", indice_lower_delay)

    current_size = already_sized.get(indice_lower_delay, "X1")

    if lower_delay < 0 and current_size != "X4":
        size = next_size(current_size)
        already_sized[indice_lower_delay] = size

        print(f"Dimensionando gate {indice_lower_delay} para {size}")

        data_arrival = np.array([])
        data_power = np.array([])

        try:
            all_combs = list(lockCombinations.generate_comb(alocated_list, already_sized))
            enven_sizes = edSizeList.Transitions(all_combs, TOTAL_GATES)
            pairs = enven_sizes.make_pairs(size, indice_lower_delay - 1)  # indice_lower_delay começa em 1
        except Exception as error:
            print(f"ERROR to search combinations {error}")
            continue

        for pair in pairs:
            sized_transition, previos_transition = pair
            id_file_sized = decoder_file_name(TOTAL_GATES, sized_transition)
            id_file_previos = decoder_file_name(TOTAL_GATES, previos_transition)

            #print(f"sized {id_file_sized} previos {id_file_previos}")
            #print(f"{v} -> {pair}")
            #v += 1

            # Busca os TXT do STA
            try:
                sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)
                sta_previos = dir.search_file(f"{id_file_previos}_{circuit}.txt", dir_out)

                #print(f"{sta_sized} - {sta_previos}")

            except Exception as error:
                print("Error to search sta files:", error)
                continue

            try:
                sta_data_sized = extData.Read_timing(sta_sized)
                ocurence_sized = sta_data_sized.count_ocurence_path()
                power_sized = sta_data_sized.get_power()
                arrivals_sized = sta_data_sized.get_arrival_times()

                sta_data_previos = extData.Read_timing(sta_previos)
                ocurence_previos = sta_data_previos.count_ocurence_path()
                power_previos = sta_data_previos.get_power()
                arrivals_previos = sta_data_previos.get_arrival_times()

         
               

            except Exception as error:
                print(f"Erro to extract STA data {error}")
                continue
            
            # atualiza as diferenças
            try:
                dif_arrival = float(list(arrivals_sized.values())[0] - list(arrivals_previos.values())[0])
                dif_power = float(power_sized - power_previos)

                data_arrival = np.append(data_arrival, dif_arrival)
                data_power = np.append(data_power, dif_power)

            except Exception as error:
                print(f"ERROR get diference {error}")

            
        # Após processar todos os pares, calcula a média e atualiza o CSV
        if len(data_arrival) > 0:
            mean_arrival = np.mean(data_arrival)
            mean_power = np.mean(data_power)

            print(f"Novo MEAN ARRIVAL gate {indice_lower_delay}: {mean_arrival}")

            try:
                ReadCSV.change_value(output_hank, "MEAN ARRIVAL", indice_lower_delay, mean_arrival)
                ReadCSV.change_value(output_hank, "MEAN POWER", indice_lower_delay, mean_power)
            except Exception as error:
                print(f"ERROR to edit CSV {error}")
        else:
            print(f"Nenhum dado coletado para gate {indice_lower_delay}")

        continue
    else:
        break