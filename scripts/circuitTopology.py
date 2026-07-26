from collections import deque
from najaeda import netlist, naja

class Circuite_topology:

    def __init__(self, verilog, libray):
        self.verilog = verilog
        self.libray = libray

        # Dicionarios da topologia do circuito 
        self.fain_gates = {}
        self.faout_gates = {}

        # Carrega o najaUniverse uma única vez e reaproveita 
        netlist.reset()
        netlist.load_liberty([self.library])
        self.top_najaeda = netlist.load_verilog([self.verilog])
        
        self.universe = naja.NLUniverse.get()
        self.top = self.universe.getTopDesign()
        
        # Eu não estou exluindo assigns nem black box's, issso pode dar problema no futuro se o verilog de entrada não estiver limpo
        self.circuit_gates = list(self.top_najaeda.get_leaf_children())

    def fain_sized_ocupation(self) -> dict:

        self.fain_gates = {}
        
        for gate in self.circuit_gates:
            gate_name = gate.get_name()
        
            visited = set()
            queue = deque([gate])
            gate_list = []  

            while queue:
                inst = queue.popleft()
                for out_term in inst.get_inputs_terms():
                    for bit_term in out_term.get_bits():
                        equipotential = bit_term.get_equipotential()
                        for reader in equipotential.get_leaf_drivers():
                            next_inst = reader.get_instance()

                            key = next_inst.get_name()
                            if key not in visited:
                                visited.add(key)
                                queue.append(next_inst)
                                gate_list.append(next_inst)  

            self.fain_gates[gate_name] = gate_list  

        return self.fain_gates
    
    def faout_sized_ocupation(self) -> dict:

        self.faout_gates = {}

        for gate in self.circuit_gates:
            gate_name = gate.get_name()

            visited = set()
            queue = deque([gate])
            gate_list = []  

            while queue:
                inst = queue.popleft()
                for out_term in inst.get_output_terms():
                    for bit_term in out_term.get_bits():
                        equipotential = bit_term.get_equipotential()
                        for reader in equipotential.get_leaf_readers():
                            next_inst = reader.get_instance()

                            key = next_inst.get_name()
                            if key not in visited:
                                visited.add(key)
                                queue.append(next_inst)
                                gate_list.append(next_inst)  

            self.faout_gates[gate_name] = gate_list  

        return self.faout_gates

                            