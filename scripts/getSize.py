def return_size(combination : list, gate_index : int):
    index = -gate_index
    gate = combination[index]

    if gate == "X1":
        return 1
    
    if gate == "X2":
        return 2
    
    if gate == "X4":
        return 4

