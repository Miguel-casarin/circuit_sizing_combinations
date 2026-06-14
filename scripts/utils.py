import os
import numpy as np

from scripts import Decoder
from scripts import  makeCSV

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

def clear_temp_dir():
    pass