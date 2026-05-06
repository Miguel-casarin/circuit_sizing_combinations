# Retorna a lista de combinações 
def total_to_size(gates_number):
    total_combination = 3 ** gates_number
    combinatios = []
    
    for i in range(total_combination):
        comb = []
        num = i

        for _ in range(gates_number):
            comb.append(num % 3)
            num //= 3

        combinatios.append(list(reversed(comb)))

    return combinatios

# Iterpleta uma combinação e retorna os valores de size
def decode_size(comb):
    mapping = {
        0 : "X1",
        1 : "X2",
        2 : "X4"
    }

    return [mapping[x] for x in comb]

def comb_list(number_gates):
    combs = total_to_size(number_gates)
    transistions = []
    for i in combs:
        dec = decode_size(i)
        transistions.append(dec)
    return transistions

def debug(number_gates):
    combs = total_to_size(number_gates)
    counter = 0
    for i in combs:
        dec = decode_size(i)
        print(f"{counter} : {i} -> {dec}")
        counter +=1 

#debug(3)