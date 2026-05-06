class Decoder:
    def __init__(self, total_cells, value_to_decode):
        self.total_cells = total_cells
        self.value_to_decode = value_to_decode

    def total_to_size(self):
        total_combinatios = 3 ** self.total_cells
        combinatios = []

        # gera todas as combinações possíveis em base 3
        for j in range(total_combinatios):
            comb = []
            num = j

            for _ in range(self.total_cells):
                comb.append(num % 3)
                num //= 3

            combinatios.append(list(reversed(comb)))

        return combinatios
    
    def decode_size(self, string_to_decode):
        mapping = {
            0 : "X1",
            1 : "X2",
            2 : "X4"
        }

        return [mapping[x] for x in string_to_decode]
    
def get_sequence(total_gates, name):
    decoder = Decoder(total_gates, name)
    list_values = decoder.total_to_size()

    if name < 0 or name >= len(list_values):
        raise ValueError("Valor a decodificar fora do intervalo permitido")

    final_value = list_values[name]
    size_values = decoder.decode_size(final_value)

    return size_values

""""
case = 700
n_gates = 6

result = get_sequence(n_gates, case)
print(f"Circuito {case}\n")
print(result)
"""