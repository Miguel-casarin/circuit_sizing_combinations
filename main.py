import os
import numpy as np
import time # Temp de execução

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

# retorna o id do arquivo dado a transição   
def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

def mean(values: list) -> float:
    return np.mean(values)

# Diretórios de busca e save
dir_out = "./output/transitions/c3"

circuit = "c3"

# Registro dos gates ja dimensionados
already_sized = {1: "X2"}

TOTAL_GATES = 3
alocated_list = [None] * TOTAL_GATES

v = 0
# Percorre todo o netlist
for indice in range(TOTAL_GATES):
    # Posição no dicionário: indice+1 (1=G1, 2=G2, 3=G3)
    gate_key = indice + 1
    print(f"\nDados{gate_key}")

    # guarda as diferenças das transições por gate  
    data_arrival = np.array([])
    data_power = np.array([])

    for size in ["X2", "X4"]:
        # Atualiza o gate atual para o size correto
        already_sized[gate_key] = size

        # Coleta todas as combinações com esse lock
        try:
            all_combs = list(lockCombinations.generate_comb(alocated_list, already_sized))
            enven_sizes = edSizeList.Transitions(all_combs, TOTAL_GATES)
            pairs = enven_sizes.make_pairs(size, indice)
        except Exception as error:
            print(f"ERROR to search combinations {error}")
            continue

        for pair in pairs:
            sized_transition, previos_transition = pair

            id_file_sized = decoder_file_name(TOTAL_GATES, sized_transition)
            id_file_previos = decoder_file_name(TOTAL_GATES, previos_transition)

            print("Debug")
            print(f"sized {id_file_sized} previos {id_file_previos}")

            print(f"{v} -> {pair}")
            v += 1

            # Busca os TXT do STA
            try:
                sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)
                sta_previos = dir.search_file(f"{id_file_previos}_{circuit}.txt", dir_out)

                print(f"{sta_sized} - {sta_previos}")

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

                print(
                        f"SIZED:\n"
                        f"{sta_data_sized}\n"
                        f"{ocurence_sized}\n"
                        f"{power_sized}\n"
                        f"{arrivals_sized}"
                    )

                print(
                        f"PREVIOS SIZED:\n"
                        f"{sta_data_previos}\n"
                        f"{ocurence_previos}\n"
                        f"{power_previos}\n"
                        f"{arrivals_previos}"
                    )

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

    # Remove o lock do gate atual antes de passar para o próximo
    del already_sized[gate_key]

    mean_arrival = np.mean(data_arrival)
    mean_power = np.mean(data_power)

    print(f"GATES {gate_key}:\n")
    print(f"Media delay = {mean_arrival}")
    print(f"Media Power = {mean_power}")