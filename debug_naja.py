import sys
import os
sys.path.append("/home/miguel/Desktop/cenaries")
from najaeda import netlist, naja

netlist.reset()
netlist.load_liberty(["./data/cells_library/Nangate45_typ.lib"])
top = netlist.load_verilog(["./data/verilogs_base/c17.v"])

gates = list(top.get_leaf_children())
print("Total gates:", len(gates))
if gates:
    gate = gates[0]
    print("Gate name:", gate.get_name())
    out_terms = list(gate.get_output_terms())
    print("Output terms:", len(out_terms))
    for out_term in out_terms:
        print(" - Term:", out_term.get_name())
        bits = list(out_term.get_bits())
        print("   Bits:", len(bits))
        for bit in bits:
            eq = bit.get_equipotential()
            print("     Eq readers:", len(list(eq.get_leaf_readers())))
            for r in eq.get_leaf_readers():
                print("       Reader:", r.get_instance().get_name())
