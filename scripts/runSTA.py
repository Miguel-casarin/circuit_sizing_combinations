import re
import subprocess
import os

from scripts import dir
from scripts import edTCL
from scripts import readV

file_tcl = "../tcl_scripts/t.tcl"
dir_circuits = 'inputs/'
dir_out = 'staOutputs/'

circuits = dir.get_files(dir_circuits)

def rename(string):
    id = re.match(r'^(.*)\.v$', string)

    if id:
        return id.group(1)

def open_sta(tcl_script, n_save, out_dir):
    n_save = f"{n_save}.txt"
    output_path = os.path.join(out_dir, n_save)

    with open(output_path, "w") as f:
          subprocess.run(
            ["sta", tcl_script],
            stdout=f,
            stderr=subprocess.STDOUT,  # STDOUT serve para mostrar os erros
            text=True
        )
          
def run_sta():
    for circuit in circuits:
        file_verilog = f"{circuit}"   

        verilog_reader = readV.Get_IO(file_verilog, dir_circuits)

        module_design = verilog_reader.verilog_module()
        inputs_sinals = verilog_reader.get_inputs()
        outputs_signals = verilog_reader.get_outputs()
        cells_name = verilog_reader.get_cells_ids()

        number_paths = edTCL.number_outputs(outputs_signals)

        design_path = f"{dir_circuits}{file_verilog}"

        script_sta = edTCL.Edit_tcl(
            file_tcl,        
            design_path,     
            module_design,   
            number_paths,    
            inputs_sinals,   
            outputs_signals  
        )

        script_sta.ed_device()
        script_sta.link_design()
        script_sta.paths_total()
        script_sta.parse_inputs()
        script_sta.parse_outputs()

        name_txt = rename(file_verilog)
        print(f"TXT name {name_txt}")

        try:
            open_sta(file_tcl, name_txt, dir_out)
            print(f"Circuit {file_verilog} analyzes in STA")
        
        except:
            print("Erro to run OpenSTA")