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

class Encoder:
    def __init__(self, size_list: list, total_gates: int):
        self.size_list = size_list
        self.total_gates = total_gates

    def encode_size(self):
        mapping = {
            "X1" : 0,
            "X2" : 1,
            "X4" : 2
        }

        return [mapping[x] for x in self.size_list]

    def base3_to_decimal(self):
        """Converte lista em base 3 para número decimal"""
        base3_list = self.encode_size()
        decimal = 0
        for digit in base3_list:
            decimal = decimal * 3 + digit
        
        return decimal
