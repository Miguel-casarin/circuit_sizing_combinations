import re
import os
import csv

def get_gates(verilog_file):
    gates = []

    with open(verilog_file, "r") as f:
        for line in f:
            line = line.strip()
            
            match = re.match(r'^\s*([A-Z0-9_]+)\s+\w+\s*\(', line)
            
            if match:
                gate = match.group(1)
                #print(f"Gate {gate} encontrada")
                gates.append(gate)

    return gates


def write_csv(netlist_list: list, csv_path: str):
    # garante que o diretório existe
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        
        # cabeçalho
        writer.writerow(["id", "area"])
        
        for i, area in enumerate(netlist_list, start=1):
            writer.writerow([i, area])

""""
verilog = "0_c2.v"
name = verilog.split(".")[0]
parent_dir = os.path.abspath("..")
csv_dir = os.path.join(parent_dir, "circuit_gates")

csv_path = os.path.join(csv_dir, f"{name}.csv")

gates = get_gates(verilog)

import area
areas = []

for gate in gates:
    a = area.search_area(gate)
    areas.append(a)

write_csv(areas, csv_path)
"""
