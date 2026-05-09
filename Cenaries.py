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


class Transitions:
    def __init__(self, combinations_list : list, number_gates : int):
        self.combinations_list = combinations_list
        self.number_gates = number_gates

    def replace_size_list(self, source_list: list, gate_index: int, to_replace: str):
        new_list = source_list.copy()
        new_list[gate_index] = to_replace.upper()
        return new_list

    def make_pairs(self, to_size : str, gate: int):
        pairs = []
        if gate <= self.number_gates:
            index_to_size = -gate
        else:
            raise ValueError("index out of range")

        for sizes_gates in self.combinations_list:
            if sizes_gates[index_to_size] == to_size:
                sized = sizes_gates
                if to_size == "X2":
                    previos_size = "X1"
                elif to_size == "X4":
                    previos_size = "X2"
                else:
                    continue

                previos_size_comb = self.replace_size_list(sizes_gates, index_to_size, previos_size)
                pairs.append((sized, previos_size_comb))

        return pairs
    
   
    def filter_other_gates(self, already_sized: list, gate_to_find: int, size: str):
        """
        Retorna pares de transições para gate_to_find no size especificado,
        apenas quando os gates em already_sized estão no mesmo size.
        
        Args:
            already_sized: Lista de índices dos gates já dimensionados
            gate_to_find: Índice do gate que se busca
            size: Tamanho desejado (ex: 'X2', 'X4')
        
        Returns:
            Lista de pares (sized, previos) que atendem aos critérios
        """
        filter_result = []
        
        # Validar índice do gate
        if gate_to_find > self.number_gates:
            raise ValueError("gate_to_find index out of range")
        
        gate_index = -gate_to_find
        
        # Obter transições para o gate_to_find no size desejado
        transitions = self.make_pairs(size, gate_to_find)
        
        # Filtrar apenas pares onde os gates em already_sized têm o mesmo size
        for pair in transitions:
            sized, previos = pair
            
            # Verificar se todos os already_sized têm o size especificado
            all_match = all(sized[-gate] == size for gate in already_sized)
            
            if all_match:
                filter_result.append(pair)
        
        return filter_result
    
def transition_stap(gate_step : int, size_step: str) -> list:
    pass 

import GatesComb


total = 6
transitions = GatesComb.comb_list(total)

generate_trasitions = Transitions(transitions, total)



gate_step = 1
size_step = "X2"
sized_memory = []

while gate_step <= total:
    print(f"\nGate dimensionado: {gate_step}")
    print(f"Gates já dimensionados: {sized_memory}")
    find = generate_trasitions.filter_other_gates(sized_memory, gate_step, size_step)
    print(f"Transições encontradas:")
    for pair in find:
        print(f"  {pair}")
    sized_memory.append(gate_step)
    gate_step += 1



