from scripts import dir
from scripts import edTCL
from scripts import extData
from scripts import readV
from scripts import runSTA


verilog_file = "./data/verilogs/0_c17.v"
script_tcl = "./tcl_scripts/t.tcl"
dir_outputs_sta = "./output/base_line/sta_base"

runSTA.run_sta(verilog_file, script_tcl, dir_outputs_sta)