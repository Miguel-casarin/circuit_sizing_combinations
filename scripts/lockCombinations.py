# interat toolys
from itertools import product
import time

inicio_timer = time.perf_counter()

def generate_comb(transitions_list, locked: dict):
    n = len(transitions_list)
    values = ["X1", "X2", "X4"]

    domains = []
    for i in range(n):
        pos_key = i + 1             # 1 = último, 2 = penúltimo, 3 = antepenúltimo...
        real_index = n - i - 1      # converte para índice real (direita → esquerda)

        if pos_key in locked:
            domains.append((locked[pos_key],))  # domínio fixo
        else:
            domains.append(tuple(values))       # domínio livre

    domains.reverse()  # reverte para manter a ordem correta na saída

    for combo in product(*domains):
        yield list(combo)


"""
n = 3
groups = [None] * n
locks = {3: "X4"}  # 1 = última posição

linha = 0
for combo in generate_comb(groups, locks):
    print(f"{linha} -> {combo}")
    linha += 1

fim_time = time.perf_counter()
print("Itertools + yield")
print(f"\nTempo TOTAL do processo: {fim_time - inicio_timer:.6f} segundos")
"""
