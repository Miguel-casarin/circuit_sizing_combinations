import os
import csv
import numpy as np

from scripts import Decoder
from scripts import makeCSV

def decoder_file_name(total_gates: int, size_list: list) -> int:
    if len(size_list) != total_gates:
        raise ValueError("total_gates range dont match size_list")
        
    encoder = Decoder.Encoder(size_list, total_gates)
    return encoder.base6_to_decimal()

def merge_size_id(drives_list: list, comb_list: list) -> list:
    merge_list = []
    try:
        for drive, comb in zip(reversed(drives_list), comb_list):
            d = f"{drive}_{comb}"
            merge_list.append(d)
    except Exception as error:
        print(f"ERROR to merge drives {error}")

    return merge_list

def find_changed_index(original: list, modified: list) -> int:
    for offset, (old, new) in enumerate(
        zip(reversed(original), reversed(modified))
    ):
        if old != new:
            return offset + 1
    return -1

def create_csv(coluns_to_make, csv_dir, csv_path):
    table = makeCSV.Create_table(coluns_to_make, csv_dir, csv_path)
    table.make_csv()

def is_dir_empty(path):
    return not any(os.scandir(path))

def mean(values: list) -> float:
    return np.mean(values)


def clear_temp_dir(verilog_maintain: str, sta_maintain: str, dir_to_clear: str) -> None:
    keep_files = {verilog_maintain, sta_maintain}
    extensions_to_remove = {".txt", ".v"}

    for file in os.listdir(dir_to_clear):
        file_path = os.path.join(dir_to_clear, file)

        if not os.path.isfile(file_path):
            continue

        _, extension = os.path.splitext(file)

        if file not in keep_files and extension in extensions_to_remove:
            os.remove(file_path)

def clear_directory(directory: str) -> None:
    extensions_to_delete = {
        ".txt",
        ".v",
        ".tcl",
    }

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        if not os.path.isfile(file_path):
            continue

        _, extension = os.path.splitext(file)

        if extension in extensions_to_delete:
            os.remove(file_path)

def combination_weight(comb: list) -> int:
    weight = 0
    for gate in comb:
        value = int(gate[1:])
        weight += value

    return weight

def update_chosen_csv(csv_path: str, target_comb: str, chosen_value: int) -> None:
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = rows[0]
    chosen_idx = header.index("CHOSEN")
    comb_idx   = header.index("COMBINATION")

    for row in rows[1:]:
        if not row:
            continue
        if row[comb_idx] == target_comb:
            row[chosen_idx] = str(chosen_value)
            break  # apenas uma linha recebe chosen = 2

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

def order_dict(original_dict: dict) -> dict:
    return dict(
        sorted(
            original_dict.items(),
            key=lambda item: int(item[0].strip('_'))
        )
    )

def dict_to_list(original_dict: dict) -> list:
    sorted_dict = order_dict(original_dict)
    return list(sorted_dict.values())

def return_gate_size(combination: list, dim_gate: int) -> int:
    gate = combination[-dim_gate]
    return int(gate[1:])