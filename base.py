from scripts import readV
from scripts import getFeatures
from scripts import extData
from scripts import runSTA


dir_circuits = './data/verilogs'
dir_out = "./output/base_line/sta_base"
tcl_file = "tcl_scripts/t.tcl"

cell_library_path = "./data/cells_library"
cells_library = "ed_Nangate.lib"
circuit = 'c17.v'

gio = readV.Get_IO(f"0_{circuit}", dir_circuits)
number_paths = len(gio.get_outputs())

# Instanciar corretamente
circuit_features = getFeatures.Circuits_features(f"0_{circuit}", dir_circuits, cells_library, cell_library_path)

deep = circuit_features.comput_deep()
print(deep)