import sys
sys.path.append('.')
from scripts.worker import Worker_combinations

class DummyGate:
    def __init__(self, name):
        self.name = name
    def get_name(self):
        return self.name

# 3 gates: G1, G2, G3
keys_list = ["G1", "G2", "G3"]
features_dict = {"G1": {}, "G2": {}, "G3": {}}
# faout_gates: G1 -> [G2], G2 -> [G3], G3 -> []
faout_gates = {
    "G1": [DummyGate("G2")],
    "G2": [DummyGate("G3")],
    "G3": []
}

# Worker init signature
worker = Worker_combinations(
    circuit="test", circuit_to_start="", temp_dir="", design_module="", design_inputs="", design_outputs="", 
    base_tcl="", drives=["type1", "type2", "type3"], json_file="data/area_json/areas.json", 
    TOTAL_GATES=3, curente_stage=["X1", "X1", "X1"], logic_types=[], 
    features_dict=features_dict, fain_gates={}, faout_gates=faout_gates
)

# G2 was resized to X2 in a previous round. Now we are testing G1 resizing to X2.
# keys_list: ["G1", "G2", "G3"]
# comb corresponds to reverse keys_list. So comb[0] is G3, comb[1] is G2, comb[2] is G1.
# G2 is X2, G1 is X2, G3 is X1
comb = ["X1", "X2", "X2"]

# dim_gate for G1: G1 is at index 0 in keys_list. So dim_gate = 1.
dim_gate = 1
print("Testing FAOUT of G1:")
res = worker.faout_ocupation(comb, dim_gate, faout_gates)
print(res)

# dim_gate for G2: G2 is at index 1 in keys_list. So dim_gate = 2.
dim_gate = 2
print("Testing FAOUT of G2:")
res2 = worker.faout_ocupation(comb, dim_gate, faout_gates)
print(res2)

