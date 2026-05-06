import re
import os

class Get_IO:
    def __init__(self, file, dir_path):
        self.file = file
        self.dir = dir_path
        self.path = os.path.join(self.dir, self.file)

    def verilog_module(self):
        
        with open(self.path, "r") as f:
            content = f.read()
            module_name = re.search(r"^\s*module\s+(\w+)", content, re.MULTILINE)

            if module_name:
                print(f"Find module {module_name.group(1)} from {self.file}")
                return module_name.group(1)
            
            else:
                return None 

    def get_inputs(self):

        inputs_list = []

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                cat_str = re.match(r'input\s+(\w+);', line)
                
                if cat_str:
                    print(f"Input {cat_str.group(1)} from file {self.file} add to list")

                    inputs_list.append(cat_str.group(1))
                
        return inputs_list   

    def get_outputs(self):

        outputs_list = []

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                cat_str = re.match(r'output\s+(\w+);', line)

                if cat_str:
                    print(f"Output {cat_str.group(1)} from {self.file} add to list")

                    outputs_list.append(cat_str.group(1)) 
                    
        return outputs_list  
    
    def get_cells_ids(self):
        
        gates_id = []

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                
                cat_str = re.match(r'\w+_X\d+\s+_(\d+)_\s*\(', line)

                if cat_str:
                    gates_id.append(cat_str.group(1))
            
            return gates_id

def debug_Get_IO(file):
    debug = Get_IO(file)

    debug.verilog_module()

    inputs = debug.get_inputs()
    for i in inputs:
        print(i)

    outputs = debug.get_outputs()
    for o in outputs:
        print(o)

    cells = debug.get_cells_ids()
    print("Cells Ids \n")
    for c in cells:
        print(c)

# Vai ser usado para automatizar o Decode em main 
def number_gates(circuit_file, dir_files):
    design = Get_IO(circuit_file, dir_files)
    return len(design.get_cells_ids())  
