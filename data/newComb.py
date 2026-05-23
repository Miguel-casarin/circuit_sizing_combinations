import re
import shutil
import os
import threading 

# Retorna a lista de combinações 
def total_to_size(gates_number):
    total_combination = 3 ** gates_number
    combinatios = []
    
    for i in range(total_combination):
        comb = []
        num = i

        for _ in range(gates_number):
            comb.append(num % 3)
            num //= 3

        combinatios.append(list(reversed(comb)))

    return combinatios

# Iterpleta uma combinação e retorna os valores de size
def decode_size(comb):
    mapping = {
        0 : "X1",
        1 : "X2",
        2 : "X4"
    }

    return [mapping[x] for x in comb]


def return_verilog_module(file):
    with open(file, encoding="utf-8") as f:
        text = f.read()

    m = re.search(r"\bmodule\s+(\w+)\s*\(", text, re.S)
    if not m:
        print("erro to copy verilog module name")
        return None

    module_name = m.group(1)
    print(f"Module name: {module_name}")
    return module_name

def get_gates(line):
    pattern = r'^(\S+\s+_\d+_)\s*\($'

    try:
        match = re.match(pattern, line)
        if match:
            return match.group(1)
    except:
        print("there is a erro during reading the cells files")


def get_cell_name(list_gates):
    ids = []
    for gate in list_gates:
        match = re.search(r'_(\d+)_', gate)
        if match:
            ids.append(match.group(1))
    return ids


def gates_from_file(verilog_file):
    module = return_verilog_module(verilog_file)
    circuit = Extract_info(
        verilog_file,
        start_block=module,
        end_block="endmodule",
        process_line=get_gates,
    )
    circuit.read_block()
    ids = get_cell_name(circuit.cells)
    return ids

# Fatia o vetor de combinações dividindo o trabalho para cada thread
def indices_to_work(intervals_list):
    total = len(intervals_list) 
    parts = total // 3

    i1 = parts
    i2 = 2 * parts

    p1 = intervals_list[:i1]
    p2 = intervals_list[i1:i2]
    p3 = intervals_list[i2:] 

    return p1, p2, p3

class Extract_info:
    def __init__(self, file, start_block, end_block, process_line):
        self.input_file = file
        self.start_block = start_block  
        self.end_block = end_block
        self.process_line = process_line
        self.cells = []

    def read_block(self):
        if not self.start_block:
            raise ValueError("start_block (module name) is None/empty")

        in_block = False
        start_re = re.compile(rf"^\s*module\s+{re.escape(self.start_block)}\b")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue

                if not in_block:
                    if start_re.match(s):
                        in_block = True
                    continue

                if s == self.end_block:
                    break

                result = self.process_line(s)
                if result:
                    self.cells.append(result)

class Edit_verilog:
    def __init__(self, original_file, output_dir):
        self.original_file = original_file
        self.output_dir = output_dir 
        
    def duplicated_and_reneme(self, new_name):
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            original = self.original_file
            new_path = os.path.join(self.output_dir, new_name)
            new = shutil.copy(original, new_path)
            if new:
                print(f"File duplicated to {new_path}\n")
                return new
                
        except Exception as e:
            print(f"error during duplication original file: {e}")

    def upsize_selected_gates(self, new_file, gate_ids_to_upsize, size):
        gate_ids_to_upsize = {str(g) for g in gate_ids_to_upsize}

        with open(new_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Ex.: "NAND2_X1 _4_ (" -> troca o "X1" por "X<size>" apenas se o id estiver selecionado.
        inst_re = re.compile(r"^(?P<lead>\s*\S+_X)(?P<x>\d+)(?P<tail>\s+_(?P<id>\d+)_\s*\()")
        edited = 0
        for i, line in enumerate(lines):
            m = inst_re.match(line)
            if not m:
                continue
            inst_id = m.group("id")
            if inst_id not in gate_ids_to_upsize:
                continue
            if m.group("x") == str(size):
                continue
            lines[i] = f"{m.group('lead')}{size}{m.group('tail')}{line[m.end():]}"
            edited += 1

        if edited:
            with open(new_file, "w", encoding="utf-8") as f:
                f.writelines(lines)
        return edited

verilog_file = f"c3.v"
design = verilog_file.split(".")[0]

parent_dir = os.path.abspath("..")
output_dir = os.path.join(parent_dir, "inputs")

ids = gates_from_file(verilog_file)
n = len(ids)

combinatios_list = total_to_size(n)

editor = Edit_verilog(verilog_file, output_dir)

def make_files(start_indice, end_indice):
    cod = start_indice 
    for combination in combinatios_list[start_indice:end_indice]:  # Usa slicing, não chamada
        size_values = decode_size(reversed(combination))  
        name_to_save = f"{cod}_{design}.v"

        new_file = editor.duplicated_and_reneme(name_to_save)

        # Mapeia cada gate para fazer o size
        ids_x1 = [gid for gid, sx in zip(ids, size_values) if sx == "X1"]
        ids_x2 = [gid for gid, sx in zip(ids, size_values) if sx == "X2"]
        ids_x4 = [gid for gid, sx in zip(ids, size_values) if sx == "X4"]

        editor.upsize_selected_gates(new_file, ids_x1, 1)
        editor.upsize_selected_gates(new_file, ids_x2, 2)
        editor.upsize_selected_gates(new_file, ids_x4, 4)

        cod += 1

# Gerenciamento das threads 
pt1, pt2, pt3 = indices_to_work(combinatios_list)

# Cria as threads corretamente
thread_1 = threading.Thread(target=make_files, args=(0, len(pt1)))
thread_2 = threading.Thread(target=make_files, args=(len(pt1), len(pt1) + len(pt2)))
thread_3 = threading.Thread(target=make_files, args=(len(pt1) + len(pt2), len(combinatios_list)))

# Inicia as threads
thread_1.start()
thread_2.start()
thread_3.start()

# Aguarda todas as threads terminarem
thread_1.join()
thread_2.join()
thread_3.join()

print("Todas as threads completaram!")