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

    def __init__(self, circuit, circuit_to_start, temp_dir, base_tcl, drives, json_file, TOTAL_GATES, curente_stage):

        self.circuit = circuit
        self.circuit_to_start = circuit_to_start
        self.temp_dir = temp_dir
        self.base_tcl = base_tcl
        self.drives = drives
        self.json_file = json_file
        self.TOTAL_GATES = TOTAL_GATES
        self.curente_stage = curente_stage
        self.fa = getArea.Get_Area(json_file)

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

    def get_timing(self, sta_data) -> float:
        arrivals = sta_data.get_arrival_times()

        return utils.mean(np.array(list(arrivals.values())))

    def get_area_cost(self, comb) -> tuple[float, int]:
        prev_drives = utils.merge_size_id(self.drives, self.curente_stage)
        prev_area = self.fa.return_total_area(prev_drives)
        comb_drives = utils.merge_size_id(self.drives, comb)
        comb_area = self.fa.return_total_area(comb_drives)
        area_cost = self.fa.cost(comb_area, prev_area)
        dim_gate    = utils.find_changed_index(self.curente_stage, comb)

        return area_cost, int(dim_gate)

    def update_stage(self, new_stage):
        self.curente_stage = new_stage

    def process(self, comb, worker_id: int) -> dict | None:
        try:
            sta_data          = self.run_sta(comb, worker_id)
            mean_arr          = self.get_timing(sta_data)
            power             = sta_data.get_power()
            area_cost, dim_gate = self.get_area_cost(comb)

            return {
                "comb":                str(comb),
                "mean_arrivals_sized": mean_arr,
                "power":               power,
                "area_cost":           area_cost,
                "dim_gate":            dim_gate,
            }
        except Exception as e:
            print(f"[Worker {worker_id}] ERRO em {comb}: {e}")
            return None