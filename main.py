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

# Diretórios de busca e save
dir_out = "./output/transitions/c3"

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

    for size in ["X2", "X4"]:
        # Atualiza o gate atual para o size correto
        already_sized[gate_key] = size

        # Coleta todas as combinações com esse lock
        try:
            all_combs = list(lockCombinations.generate_comb(alocated_list, already_sized))

            enven_sizes = edSizeList.Transitions(all_combs, TOTAL_GATES)
            pairs = enven_sizes.make_pairs(size, indice)

            for pair in pairs:
                sized_transition, previos_transition = pair
                id_file_sized = decoder_file_name(TOTAL_GATES, sized_transition)
                id_file_previos = decoder_file_name(TOTAL_GATES, previos_transition)

                print("Debug")
                print(f"sized {id_file_sized} previos {id_file_previos}")

                print(f"{v} -> {pair}")
                v += 1

               
        except Exception as error:
            print(f"ERROR to search combinations {error}")


        #try:
        #except Exception as error:
            #print(f"ERROR to process STA file {error}")

    # Remove o lock do gate atual antes de passar para o próximo
    del already_sized[gate_key]