"""
Recriação standalone do Cenaries.py
- Simula GatesComb e Decoder sem dependências externas
- Imprime todas as transições passo a passo
"""

import itertools

# ─────────────────────────────────────────────
# Simulação de GatesComb
# ─────────────────────────────────────────────
SIZES = ["X1", "X2", "X4"]

def comb_list(total_gates: int) -> list:
    """Gera todas as combinações de sizes para N gates."""
    return [list(c) for c in itertools.product(SIZES, repeat=total_gates)]


# ─────────────────────────────────────────────
# Simulação de Decoder
# ─────────────────────────────────────────────
def decoder_file_name(total_gates: int, size_list: list) -> int:
    """Converte lista de sizes para um ID numérico (base 3)."""
    size_to_int = {"X1": 0, "X2": 1, "X4": 2}
    result = 0
    for s in size_list:
        result = result * 3 + size_to_int[s]
    return result


# ─────────────────────────────────────────────
# Classe Transitions
# ─────────────────────────────────────────────
class Transitions:
    def __init__(self, combinations_list: list, number_gates: int):
        self.combinations_list = combinations_list
        self.number_gates = number_gates

    def replace_size_list(self, source_list: list, gate_index: int, to_replace: str):
        new_list = source_list.copy()
        new_list[gate_index] = to_replace.upper()
        return new_list

    def make_pairs(self, to_size: str, gate: int):
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

    def filter_other_gates(self, already_sized: list, gate_to_find: int, size: str):
        filter_result = []

        if gate_to_find > self.number_gates:
            raise ValueError("gate_to_find index out of range")

        transitions = self.make_pairs(size, gate_to_find)

        for pair in transitions:
            sized, previos = pair
            all_match = all(sized[-gate] == size for gate in already_sized)
            if all_match:
                filter_result.append(pair)

        return filter_result


# ─────────────────────────────────────────────
# Helpers de print
# ─────────────────────────────────────────────
def fmt_comb(comb: list) -> str:
    return "[" + ", ".join(comb) + "]"

def print_header(text: str):
    print("\n" + "═" * 55)
    print(f"  {text}")
    print("═" * 55)

def print_section(text: str):
    print("\n" + "─" * 45)
    print(f"  {text}")
    print("─" * 45)

def print_pair(i: int, sized: list, previos: list, id_sized: int, id_previos: int):
    print(f"  Par {i+1}:")
    print(f"    sized   → ID {id_sized:>4}  {fmt_comb(sized)}")
    print(f"    previos → ID {id_previos:>4}  {fmt_comb(previos)}")


# ─────────────────────────────────────────────
# Configuração
# ─────────────────────────────────────────────
TOTAL        = 6         # Número de gates (mude aqui para testar)
size_step    = "X2"       # Size alvo (X2 ou X4)
circuit_name = "c17"

combinations = comb_list(TOTAL)
transitions  = Transitions(combinations, TOTAL)

print_header(f"COMBINAÇÕES GERADAS  (TOTAL={TOTAL} gates, {len(combinations)} combinações)")
for idx, comb in enumerate(combinations):
    print(f"  ID {idx:>3}  {fmt_comb(comb)}")


# ─────────────────────────────────────────────
# Loop principal: dimensiona gate a gate
# ─────────────────────────────────────────────
sized_memory = []

for gate_step in range(1, TOTAL + 1):

    print_header(f"GATE {gate_step}  |  sized_memory antes = {sized_memory}")

    # ── Todas as transições brutas para este gate ──
    all_pairs = transitions.make_pairs(size_step, gate_step)
    print(f"\n  [make_pairs] Todas as transições para G{gate_step} → {size_step}:  ({len(all_pairs)} pares)")
    for i, (sz, pv) in enumerate(all_pairs):
        id_sz = decoder_file_name(TOTAL, sz)
        id_pv = decoder_file_name(TOTAL, pv)
        print_pair(i, sz, pv, id_sz, id_pv)

    # ── Após filtro pelos gates já fixos ──
    filtered = transitions.filter_other_gates(sized_memory, gate_step, size_step)

    if sized_memory:
        print_section(
            f"[filter_other_gates] Filtrando onde {sized_memory} estão em {size_step}  →  {len(filtered)} pares restantes"
        )
    else:
        print_section(f"[filter_other_gates] Nenhum filtro aplicado (sized_memory vazio)  →  {len(filtered)} pares")

    if not filtered:
        print("  ⚠  Nenhum par encontrado após filtro.")
    else:
        for i, (sz, pv) in enumerate(filtered):
            id_sz = decoder_file_name(TOTAL, sz)
            id_pv = decoder_file_name(TOTAL, pv)
            print_pair(i, sz, pv, id_sz, id_pv)

    # ── Simula cálculo de deltas ──
    print(f"\n  [deltas simulados]")
    for i, (sz, pv) in enumerate(filtered):
        id_sz = decoder_file_name(TOTAL, sz)
        id_pv = decoder_file_name(TOTAL, pv)
        print(f"    Par {i+1}: arquivo {id_sz}_{circuit_name}.v  →  {id_pv}_{circuit_name}.v")

    # ── Adiciona à memória ──
    sized_memory.append(gate_step)
    print(f"\n  ✔  G{gate_step} fixado. sized_memory agora = {sized_memory}")


print_header("FIM  —  Todos os gates dimensionados")
print(f"  Ordem de dimensionamento: {sized_memory}\n")