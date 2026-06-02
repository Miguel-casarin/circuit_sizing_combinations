
class Make_transitions:

    def __init__(self,size_order):
        self.size_order = size_order

    def base_transitions(self, number_gates: int) -> list:
        result = []
        
        for i in range(number_gates):
            temp = ["X1"] * number_gates
            temp[-(i + 1)] = "X2"   # começa pelo final
            result.append(temp)

        return result

    def transitions(self, current_combination: list) -> list:
    
        result = []

        for i, element in enumerate(current_combination):
            current_index = self.size_order.index(element)

            # Só avança se não for o último tamanho
            if current_index < len(self.size_order) - 1:
                next_size = self.size_order[current_index + 1]

                new_combination = current_combination.copy()
                new_combination[i] = next_size  # avança só a posição i

                if new_combination not in result:
                    result.append(new_combination)

        return result
    
    def valid_transitions(self, candidates: list, cells_drive: list, libray) -> list:
        valid = []
        reversed_drives = cells_drive[::-1]
        for comb in candidates:
            comb_valid = True
            for cell, size in zip(reversed_drives, comb):
                key = cell + "_" + size
                if key not in libray:
                    comb_valid = False
                    break
            if comb_valid:
                valid.append(comb)
        
        return valid
    
    def get_base_transitions(self, number_gates: int, cells_drive: list, libray):
        candidates = self.base_transitions(number_gates)
        return self.valid_transitions(candidates, cells_drive, libray)

    def get_transitions(self, current_combination: list, cells_drive: list, libray):
        candidates = self.transitions(current_combination)
        return self.valid_transitions(candidates, cells_drive, libray)