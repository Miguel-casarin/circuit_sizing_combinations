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
from scripts import Decoder

import GatesComb

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

# retorna o id do arquivo dado a transição   
def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates rabge dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base3_to_decimal()

def is_dir_empty(path):
    return not any(os.scandir(path))

def mean(values: list) -> float:
    return np.mean(values)

def create_csv(coluns_to_make: str, csv_dir, csv_path):
    table = makeCSV.Create_table(coluns_to_make, csv_dir, csv_path)
    table.make_csv()  


def map_gate(gate_to_map: int, verilog) -> str:
    map_netlist = getNetlist.get_gates(verilog)
    index = gate_to_map -1
    return map_netlist[index]

def cost_area(gate_to_map: int, verilog, json) -> float:
    maped = map_gate(gate_to_map, verilog)

    current_map = getArea.search_area(maped, json)
    previos_map = getArea.get_previous_area(maped, json)

    cost = getArea.cost_area(current_map, previos_map)

    return cost
                
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

dir_circuits = './data/verilogs/c17'
dir_out = "./output/transitions/c17"
tcl_file = "tcl_scripts/t.tcl"

json_dir = "./data/area_json"
json_areas = "areas_nangate.json"
path_json_areas = os.path.join(json_dir, json_areas)

circuit = "c17"
base_verilog_path = './data/verilogs_base'

if is_dir_empty(dir_out):
    runSTA.run_sta(dir_circuits, dir_out, tcl_file)

try: 
    gio = readV.Get_IO(f"0_{circuit}.v", base_verilog_path)
    cells_id = gio.get_cells_ids()

    TOTAL = len(cells_id)
    NUMBER_OUTPUTS = len(gio.get_outputs())
except Exception as error:
    print(f"Error to read base line verilog {error}")

# Obtendo features bases do designg
try:

    circuit_features = getFeatures.Circuits_features(f"0_{circuit}.v", base_verilog_path, cells_library, cell_library_path)

    fa_in = circuit_features.fan_in()
    fa_out = circuit_features.fan_out()
    ln = circuit_features.compute_logic_levels()
    deep = circuit_features.comput_deep()
    
except Exception as error:
    print(f"Error to get features {error}")


transitions = GatesComb.comb_list(TOTAL)
generate_trasitions = Transitions(transitions, TOTAL)

size_step = "X2"
gate_inicial = 1  # Escolha qual gate começar
sized_memory = []

gate = cells_id[gate_inicial - 1]

# Primeiro dimensiona o gate inicial
print(f"\nGate dimensionado: {gate_inicial}")
print(f"Gates já dimensionados: {sized_memory}")
find = generate_trasitions.filter_other_gates(sized_memory, gate_inicial, size_step)
print(f"Transições encontradas:")


power_dif = np.array([])
arrival_dif = np.array([])

for pair in find:
    print(f"{pair}")

   

    sized_transition, previos_transition = pair
    id_file_sized = decoder_file_name(TOTAL, sized_transition)
    id_file_previos = decoder_file_name(TOTAL, previos_transition)

    # Busca os verilogs
    try:
        verilog_sized = dir.search_file(f"{id_file_sized}_{circuit}.v", dir_circuits)
        verilog_previos = dir.search_file(f"{id_file_previos}_{circuit}.v", dir_circuits)
    except Exception as error:
        print("Error to search verilog files:", error)
        continue

        
    # Busca os TXT do STA
    try:
        sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)
        sta_previos = dir.search_file(f"{id_file_previos}_{circuit}.txt", dir_out)
    except Exception as error:
        print("Error to search sta files:", error)
        continue

    try:
        sta_data_sized = extData.Read_timing(sta_sized)
        ocurence_sized = sta_data_sized.count_ocurence_path()
        power_sized = sta_data_sized.get_power()
        print(f"Power sized: {power_sized}")

        arrivals_sized = sta_data_sized.get_arrival_times()
        arrivals_values_sized = np.array(list(arrivals_sized.values()))
        mean_arrivals_sized = mean(arrivals_values_sized)

        sta_data_previos = extData.Read_timing(sta_previos)
        #ocurence_previos = sta_data_previos.count_ocurence_path()
        power_previos = sta_data_previos.get_power()
        print(f"Power previos: {power_previos}")

        arrivals_previos = sta_data_previos.get_arrival_times()
        arrivals_values_previos = np.array(list(arrivals_previos.values()))
        mean_arrivals_previos = mean(arrivals_values_previos)

    except Exception as error:
        print(f"Erro to extract STA data {error}")
        continue

    # media das diferenças 
    try:
        dif_power = float(power_sized) - float(power_previos)
        power_dif = np.append(power_dif, dif_power)

        dif_arrival = float(mean_arrivals_sized) - float(mean_arrivals_previos)
        arrival_dif = np.append(arrival_dif, dif_arrival)


        
        

    except Exception as error:
        print(f"Error on get mean diferences {error}")

    print(f"{id_file_sized} - {id_file_previos}")

try:
    mean_power_dif = mean(power_dif)
    mean_arrival_dif = mean(arrival_dif)

  
    print(f"    Média Power Diff: {mean_power_dif}")
    print(f"    Média Arrival Diff: {mean_arrival_dif}")
except Exception as error:
    print(f"Error to get mean differences {error}")

sized_memory.append(gate_inicial)













# Depois dimensiona todos os demais gates mantendo o inicial fixo
for gate_step in range(1, TOTAL + 1):
    if gate_step != gate_inicial:  # Pula o gate inicial já processado

        power_dif = np.array([])
        arrival_dif = np.array([])

        # gate do circuito sendo dimensionado
        gate = cells_id[gate_step - 1]  # Ajustar índice (0-based)
        print(f"\nGate dimensionado: {gate_step} ({gate})")

        print(f"Gates já dimensionados: {sized_memory}")
        find = generate_trasitions.filter_other_gates(sized_memory, gate_step, size_step)
        print(f"Transições encontradas:")
        for pair in find:
            print(f"  {pair}")

            sized_transition, previos_transition = pair
            id_file_sized = decoder_file_name(TOTAL, sized_transition)
            id_file_previos = decoder_file_name(TOTAL, previos_transition)
            print(f"{id_file_sized} - {id_file_previos}")

            # Busca os verilogs
            try:
                verilog_sized = dir.search_file(f"{id_file_sized}_{circuit}.v", dir_circuits)
                verilog_previos = dir.search_file(f"{id_file_previos}_{circuit}.v", dir_circuits)
            except Exception as error:
                print("Error to search verilog files:", error)
                continue
        
            # Busca os TXT do STA
            try:
                sta_sized = dir.search_file(f"{id_file_sized}_{circuit}.txt", dir_out)
                sta_previos = dir.search_file(f"{id_file_previos}_{circuit}.txt", dir_out)
            except Exception as error:
                print("Error to search sta files:", error)
                continue

            try:
                sta_data_sized = extData.Read_timing(sta_sized)
                ocurence_sized = sta_data_sized.count_ocurence_path()
                power_sized = sta_data_sized.get_power()
                print(f"Power sized: {power_sized}")

                arrivals_sized = sta_data_sized.get_arrival_times()
                arrivals_values_sized = np.array(list(arrivals_sized.values()))
                mean_arrivals_sized = mean(arrivals_values_sized)

                sta_data_previos = extData.Read_timing(sta_previos)
                #ocurence_previos = sta_data_previos.count_ocurence_path()
                power_previos = sta_data_previos.get_power()
                print(f"Power previos: {power_previos}")

                arrivals_previos = sta_data_previos.get_arrival_times()
                arrivals_values_previos = np.array(list(arrivals_previos.values()))
                mean_arrivals_previos = mean(arrivals_values_previos)

            except Exception as error:
                print(f"Erro to extract STA data {error}")
                continue

            # media das diferenças 
            try:
                dif_power = float(power_sized) - float(power_previos)
                power_dif = np.append(power_dif, dif_power)

                dif_arrival = float(mean_arrivals_sized) - float(mean_arrivals_previos)
                arrival_dif = np.append(arrival_dif, dif_arrival)
                
            except Exception as error:
                print(f"Error on get mean diferences {error}")

          

        # Calcular e exibir as médias após processar todos os pares
        try:
            mean_power_dif = mean(power_dif)
            mean_arrival_dif = mean(arrival_dif)

            print(f"    Média Power Diff: {mean_power_dif:.2e}")
            print(f"    Média Arrival Diff: {mean_arrival_dif:.6f}")
        except Exception as error:
            print(f"Error to get mean differences {error}")
           
        sized_memory.append(gate_step)




