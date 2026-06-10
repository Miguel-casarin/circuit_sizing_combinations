import os
import numpy as np

from scripts import utils
from scripts import setCombination
from scripts import singleSTA
from scripts import extData
from scripts import dir
from scripts import getArea

def verilog_and_sta(comb, circuit_to_start, temp, tcl_file, circuit, total_gates):
    
    id_file_sized = utils.decoder_file_name(total_gates, comb)
    name_to_save = f"{id_file_sized}_{circuit}.v"
    comb_temp = os.path.join(temp, str(id_file_sized))
    os.makedirs(comb_temp, exist_ok=True)

    try:
        setCombination.apply_combination(circuit_to_start, comb_temp, comb, name_to_save)
        singleSTA.run_single(tcl_file, name_to_save, comb_temp, comb_temp)
    except Exception as e:
        print(f"ERROR STA {comb}: {e}")
        return None

    return {'comb': comb, 'id_file_sized': id_file_sized, 'comb_temp': comb_temp}


def read_sta_results(sta_result, circuit, drives, json_file, curente_stage):
    comb = sta_result['comb']
    id_file = sta_result['id_file_sized']
    comb_temp = sta_result['comb_temp']

    try:
        sta_file = dir.search_file(f"{id_file}_{circuit}.txt", comb_temp)
        sta_data = extData.Read_timing(sta_file)

        arrivals = sta_data.get_arrival_times()
        mean_arrivals = utils.mean(np.array(list(arrivals.values())))
        power = sta_data.get_power()

        fa = getArea.Get_Area(json_file)

        comb_drives = utils.merge_size_id(drives, comb)
        comb_area = fa.return_total_area(comb_drives)

        previos_comb = utils.merge_size_id(drives, curente_stage)
        previos_area = fa.return_total_area(previos_comb)

        area_cost = fa.cost(comb_area, previos_area)
        dim_gate = utils.find_changed_index(curente_stage, comb)
    except Exception as e:
        print(f"ERROR reading results {comb}: {e}")
        return None

    return {
        'comb': comb,
        'mean_arrivals_sized': mean_arrivals,
        'power': power,
        'area_cost': area_cost,
        'dim_gate': dim_gate,
    }