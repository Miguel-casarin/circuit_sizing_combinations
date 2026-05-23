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