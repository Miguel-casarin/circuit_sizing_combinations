import os
import numpy as np 
import shutil

from scripts import extData
from scripts import singleSTA
from scripts import dir
from scripts import setCombination
from scripts import getArea
from scripts import utils

class Worker_combinations:

    def __init__(self, circuit, circuit_to_start, temp_dir, base_tcl, drives, json_file, TOTAL_GATES, curente_stage, fain_list, faout_list, logic_level_list, deep_list):

        self.circuit = circuit
        self.circuit_to_start = circuit_to_start
        self.temp_dir = temp_dir
        self.base_tcl = base_tcl
        self.drives = drives
        self.json_file = json_file
        self.TOTAL_GATES = TOTAL_GATES
        self.curente_stage = curente_stage
        self.fa = getArea.Get_Area(json_file)
        self.fain_list        = fain_list
        self.faout_list       = faout_list
        self.logic_level_list = logic_level_list
        self.deep_list        = deep_list

    def get_worker_tcl(self, worker_id: int) -> str:
        worker_tcl = os.path.join(self.temp_dir, f"t_worker_{worker_id}.tcl")
        if not os.path.exists(worker_tcl):
            shutil.copy(self.base_tcl, worker_tcl)
        return worker_tcl

    def run_sta(self, comb, work_id: int):
        worker_tcl = self.get_worker_tcl(work_id)
        id_file_sized = utils.decoder_file_name(self.TOTAL_GATES, comb)
        name_to_save  = f"{id_file_sized}_{self.circuit}.v"

        setCombination.apply_combination(self.circuit_to_start, self.temp_dir, comb, name_to_save)
        singleSTA.run_single(worker_tcl, name_to_save, self.temp_dir, self.temp_dir)

        sta_path = dir.search_file(f"{id_file_sized}_{self.circuit}.txt", self.temp_dir)

        return extData.Read_timing(sta_path)

    def size_weight(self, comb) -> int:
        return utils.combination_weight(comb)
    
    def get_timing(self, sta_data) -> float:
        arrivals = sta_data.get_arrival_times()

        return utils.mean(np.array(list(arrivals.values())))

    def get_prev_drives(self) -> list:
        return utils.merge_size_id(self.drives, self.curente_stage)

    def get_comb_drives(self, comb) -> list:
        return utils.merge_size_id(self.drives, comb)

    def get_prev_area(self) -> float:
        prev_drives = self.get_prev_drives()
        return self.fa.return_total_area(prev_drives)

    def get_comb_area(self, comb) -> float:
        comb_drives = self.get_comb_drives(comb)
        return self.fa.return_total_area(comb_drives)

    def get_area_cost(self, comb) -> float:
        prev_area = self.get_prev_area()
        comb_area = self.get_comb_area(comb)
        return self.fa.cost(comb_area, prev_area)

    def get_dim_gate(self, comb) -> int:
        return utils.find_changed_index(self.curente_stage, comb)

    def fa_in(self, dim_gate: int) -> int:
        return self.fain_list[dim_gate - 1]

    def fa_out(self, dim_gate: int) -> int:
        return self.faout_list[dim_gate - 1]

    def logic_level(self, dim_gate: int) -> int:
        return self.logic_level_list[dim_gate - 1]

    def deep(self, dim_gate: int) -> int:
        return self.deep_list[dim_gate - 1]

    def size_dim(self, comb: list, dim_gate: int) -> int:
        return utils.return_gate_size(comb, dim_gate)

    def update_stage(self, new_stage):
        self.curente_stage = new_stage

    def process(self, comb, worker_id: int) -> dict | None:
        try:
            sta_data  = self.run_sta(comb, worker_id)
            mean_arr  = self.get_timing(sta_data)
            power     = sta_data.get_power()
            dim_gate  = self.get_dim_gate(comb)

            return {
                "comb":                comb,
                "size":                self.size_dim(comb, dim_gate),
                "size_weight":         self.size_weight(comb),
                "mean_arrivals_sized": mean_arr,
                "power":               power,
                "area_cost":           self.get_area_cost(comb),
                "dim_gate":            dim_gate,
                "prev_drives":         self.get_prev_drives(),
                "comb_drives":         self.get_comb_drives(comb),
                "prev_area":           self.get_prev_area(),
                "comb_area":           self.get_comb_area(comb),
                "fa_in":               self.fa_in(dim_gate),
                "fa_out":              self.fa_out(dim_gate),
                "logic_level":         self.logic_level(dim_gate),
                "deep":                self.deep(dim_gate),
            }
        except Exception as error:
            print(f"[Worker {worker_id}] ERRO em {comb}: {error}")
            return None