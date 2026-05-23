def return_size(combination : list, gate_index : int):
    index = -gate_index
    gate = combination[index]

    if gate == "X1":
        return 1
    
    if gate == "X2":
        return 2
    
    if gate == "X4":
        return 4

def return_single_size(size_str: str) -> int:
    if size_str == "X1":
        return 1
    
    if size_str == "X2":
        return 2
    
    if size_str == "X4":
        return 4