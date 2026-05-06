import os

from scripts import dir
from scripts import edTCL
from scripts import extData
from scripts import readV
from scripts import runSTA

# Usa caminhos absolutos baseados no diretório do script
base_dir = os.path.dirname(os.path.abspath(__file__))
dir_circuits = os.path.join(base_dir, "base_line", "imputs")
design_dir = os.path.join(base_dir, "base_line", "sta")
verilog = "c17.v"

def is_dir_empty(path) -> bool:
    return not any(os.scandir(path))

if is_dir_empty(design_dir):
    runSTA.run_sta()
