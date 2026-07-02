from collections import deque
import os 
from najaeda import netlist, naja

#netlist.reset()
#netlist.load_liberty(["Nangate45_typ.lib"])
#top = netlist.load_verilog(["c17.v"])

#def explore_design(instance):    
    #print(f"{instance.get_name()} with model: {instance.get_model_name()}")    
    #for ins in instance.get_child_instances():        
        #explore_design(ins)
        
#explore_design(top)

class Netlist_info:
    def __init__(self, verilog, verilog_path,  libray, libraey_path):
        self.verilog = verilog
        self.verilog_path = verilog_path
        self.path_v = os.path.join(self.verilog_path, self.verilog)
        
        self.libray = libray
        self.libray_path = libraey_path
        self.path_lib = os.path.join(self.libray_path, self.libray)
    
    def print_nets(self):
        netlist.reset()
        netlist.load_liberty([self.path_lib])
        top = netlist.load_verilog([self.path_v])

        for inst in top.get_child_instances():
            print(f"Instance {inst.get_name()}")
            for term in inst.get_terms():
                print(f"  Pin: {term.get_name()} ({term.get_direction()})")
                print(f"    Net: {term.get_upper_net().get_name()}")
                
    
class Circuits_features:
    def __init__(self, verilog, verilog_path,  libray, libraey_path):
        self.verilog = verilog
        self.verilog_path = verilog_path
        self.path_v = os.path.join(self.verilog_path, self.verilog)
        
        self.libray = libray
        self.libray_path = libraey_path
        self.path_lib = os.path.join(self.libray_path, self.libray)

    def compute_logic_levels(self):
        netlist.reset()
        netlist.load_liberty([self.path_lib])
        netlist.load_verilog([self.path_v])

        # Usa a API NL/SNL da versão atual do najaeda
        universe = naja.NLUniverse.get()
        top = universe.getTopDesign()

        # mapeia:
        #  - inst_name -> instância
        #  - inst_name -> conjunto de nets de entrada
        instances = {}
        inst_inputs = {}

        for inst in top.getInstances():
            name = inst.getName()
            instances[name] = inst
            in_nets = set()
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Input:
                    continue
                net = term.getNet()
                if net:
                    in_nets.add(net)
            inst_inputs[name] = in_nets

        # conjunto de nets ligadas diretamente às entradas primárias (PIs)
        pi_nets = set()
        for term in top.getBitTerms():
            if term.getDirection() != naja.SNLTerm.Direction.Input:
                continue
            net = term.getNet()
            if net:
                pi_nets.add(net)

        # mapeia net -> instâncias que a dirigem (fanin)
        net_drivers = {}
        for inst in top.getInstances():
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Output:
                    continue
                net = term.getNet()
                if not net:
                    continue
                net_drivers.setdefault(net, set()).add(inst)

        levels = {}
        changed = True

        while changed:
            changed = False
            for inst_name, in_nets in inst_inputs.items():
                if inst_name in levels:
                    continue

                all_from_pi = True
                drivers_levels = []
                resolvable = True

                for net in in_nets:
                    if net in pi_nets:
                        continue  # entrada primária, ok

                    all_from_pi = False
                    drivers = net_drivers.get(net, set())
                    if not drivers:
                        resolvable = False
                        break

                    local_levels = []
                    for drv in drivers:
                        drv_name = drv.getName()
                        if drv_name not in levels:
                            resolvable = False
                            break
                        local_levels.append(levels[drv_name])

                    if not resolvable:
                        break

                    drivers_levels.append(max(local_levels))

                if not resolvable:
                    continue

                if all_from_pi:
                    levels[inst_name] = 1
                else:
                    levels[inst_name] = max(drivers_levels) + 1

                changed = True

        return levels

    def comput_deep(self):
        netlist.reset()
        netlist.load_liberty([self.path_lib])
        netlist.load_verilog([self.path_v])

        universe = naja.NLUniverse.get()
        top = universe.getTopDesign()

        # mapeia instâncias e suas nets de saída
        inst_outputs = {}
        for inst in top.getInstances():
            name = inst.getName()
            out_nets = set()
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Output:
                    continue
                net = term.getNet()
                if net:
                    out_nets.add(net)
            inst_outputs[name] = out_nets

        # nets ligadas diretamente às saídas primárias (POs)
        po_nets = set()
        for term in top.getBitTerms():
            if term.getDirection() != naja.SNLTerm.Direction.Output:
                continue
            net = term.getNet()
            if net:
                po_nets.add(net)

        # mapeia net -> instâncias que usam essa net como ENTRADA (fanout)
        net_users = {}
        for inst in top.getInstances():
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Input:
                    continue
                net = term.getNet()
                if not net:
                    continue
                net_users.setdefault(net, set()).add(inst)

        deep = {}

        # 1) gates diretamente ligados a uma saída primária: deep = 1
        for inst_name, out_nets in inst_outputs.items():
            if any(net in po_nets for net in out_nets):
                deep[inst_name] = 1

        # 2) propaga para trás: deep = 1 + max(deep dos fanouts)
        changed = True
        while changed:
            changed = False
            for inst_name, out_nets in inst_outputs.items():
                if inst_name in deep:
                    continue

                resolvable = True
                fanout_deeps = []

                for net in out_nets:
                    users = net_users.get(net, set())
                    if not users:
                        # net que não leva a lugar nenhum não contribui
                        continue

                    local = []
                    for u in users:
                        u_name = u.getName()
                        if u_name not in deep:
                            resolvable = False
                            break
                        local.append(deep[u_name])

                    if not resolvable:
                        break

                    if local:
                        fanout_deeps.append(max(local))

                if not resolvable or not fanout_deeps:
                    continue

                deep[inst_name] = max(fanout_deeps) + 1
                changed = True

        return deep

    def fan_in(self):
        netlist.reset()
        netlist.load_liberty([self.path_lib])
        netlist.load_verilog([self.path_v])

        universe = naja.NLUniverse.get()
        top = universe.getTopDesign()

        fanin_counts = {}

        # para cada instância, conta quantos pinos de entrada ela possui
        for inst in top.getInstances():
            name = inst.getName()
            count = 0
            for term in inst.getInstTerms():
                if term.getDirection() == naja.SNLTerm.Direction.Input:
                    count += 1
            fanin_counts[name] = count

        return fanin_counts


    def fan_out(self):
        netlist.reset()
        netlist.load_liberty([self.path_lib])
        netlist.load_verilog([self.path_v])

        universe = naja.NLUniverse.get()
        top = universe.getTopDesign()

        # mapeia, para cada instância, quais nets ela dirige (saídas)
        inst_outputs = {}
        for inst in top.getInstances():
            name = inst.getName()
            out_nets = set()
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Output:
                    continue
                net = term.getNet()
                if net:
                    out_nets.add(net)
            inst_outputs[name] = out_nets

        # mapeia net -> instâncias que usam essa net como entrada (fanout físico)
        net_users = {}
        for inst in top.getInstances():
            for term in inst.getInstTerms():
                if term.getDirection() != naja.SNLTerm.Direction.Input:
                    continue
                net = term.getNet()
                if not net:
                    continue
                net_users.setdefault(net, set()).add(inst.getName())

        # fan-out em número de gates: quantos gates recebem essa saída
        fanout_counts = {}
        for inst_name, out_nets in inst_outputs.items():
            destinations = set()
            for net in out_nets:
                for user_name in net_users.get(net, set()):
                    if user_name != inst_name:  # evita contar auto-loop estranho
                        destinations.add(user_name)
            fanout_counts[inst_name] = len(destinations)

        return fanout_counts

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
verilog_path = os.path.join(base_dir, "data", "verilogs_base") 
verilog = "c17.v"
lib_path = os.path.join(base_dir, "data", "cells_library") 
lib = "ed_Nangate.lib"

try:
    f = Circuits_features(verilog, verilog_path, lib, lib_path)

    fanin = f.fan_in()
    faout = f.fan_out()
    logic_level = f.compute_logic_levels()
    deep = f.comput_deep()
except Exception as error:
    print(error)

print("FAnin")
print(fanin)
print("FAout")
print(faout)
print("level")
print(logic_level)
print("DEEP")
print(deep)
