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

# Registro dos gates ja dimensionados
already_sized = {1: "X2"}

TOTAL_GATES = 3
alocated_list = [None] * TOTAL_GATES

v = 0
for size in ["X2", "X4"]:
    already_sized[1] = size  # atualiza a chave 1 diretamente
    print(f"\n--- Rodando com posição 1 = {size} ---")
    for comb in lockCombinations.generate_comb(alocated_list, already_sized):
        print(f"{v} -> {comb}")
        v += 1
