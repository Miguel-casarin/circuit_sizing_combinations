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
    
    # Recebe o gate base a sua transição, retorna demais transições do circuito com o gate base fixo
    def filter_other_gates(self, base_gate: int, base_gate_size: str, other_gate: int):

        filter = []

        if base_gate and other_gate <= self.number_gates:
            base_index = -base_gate
            
        other_gates_transitions = self.make_pairs(base_gate_size, other_gate)
        
        for pair in other_gates_transitions:
            sized, previos = pair
            if sized[base_index] == base_gate_size and previos[base_index] == base_gate_size:
                filter.append(pair)

        return filter
    
def transition_stap(gate_step : int, size_step: str) -> list:
    pass 

import GatesComb

total = 2
transitions = GatesComb.comb_list(2)

circuito = Transitions(transitions, total)

base = circuito.make_pairs("X4", 1)

# usar quando for dimensionar outro gate mas mantendo gates anteriores ja dimensionados
o = circuito.filter_other_gates(1, "X4", 2)

for j, k in base:
    print(f"{j}  - {k}")

for j, k in o:
    print(f"{j}  - {k} *")