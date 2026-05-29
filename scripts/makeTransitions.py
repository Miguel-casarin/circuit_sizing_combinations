
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