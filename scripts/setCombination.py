import os
import re
import shutil


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

    def duplicated_and_rename(self, new_name):
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            new_path = os.path.join(self.output_dir, new_name)
            new = shutil.copy(self.original_file, new_path)
            if new:
                print(f"File duplicated to {new_path}\n")
                return new

        except Exception as e:
            print(f"Error during duplication of original file: {e}")

    def upsize_selected_gates(self, new_file, gate_ids_to_upsize, size):
        gate_ids_to_upsize = {str(g) for g in gate_ids_to_upsize}

        with open(new_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Ex.: "NAND2_X1 _4_ (" -> replaces "X1" with "X<size>" only if id is selected
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


def decode_size(string_comb):
    """Maps size strings like 'X1', 'X2', 'X4' to their integer values."""
    mapping = {
        "X1": 1,
        "X2": 2,
        "X4": 4,
        "X8": 8,
        "X16": 16,
        "X32": 32
    }
    return [mapping[x] for x in string_comb]


def return_verilog_module(file):
    with open(file, encoding="utf-8") as f:
        text = f.read()

    m = re.search(r"\bmodule\s+(\w+)\s*\(", text, re.S)
    if not m:
        print("Error: could not find verilog module name")
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
    except Exception:
        print("Error during reading the cells")


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


def apply_combination(verilog_file, output_dir, combination, output_name):
   
    ids = gates_from_file(verilog_file)

    if len(ids) != len(combination):
        raise ValueError(
            f"Combination length ({len(combination)}) does not match "
            f"number of gates in file ({len(ids)})."
        )

    editor = Edit_verilog(verilog_file, output_dir)
    new_file = editor.duplicated_and_rename(output_name)
    

    size_values = decode_size(combination)

    ids_reversed = list(reversed(ids))
 
    ids_x1 = [gid for gid, sx in zip(ids_reversed, size_values) if sx == 1]
    ids_x2 = [gid for gid, sx in zip(ids_reversed, size_values) if sx == 2]
    ids_x4 = [gid for gid, sx in zip(ids_reversed, size_values) if sx == 4]


    editor.upsize_selected_gates(new_file, ids_x1, 1)
    editor.upsize_selected_gates(new_file, ids_x2, 2)
    editor.upsize_selected_gates(new_file, ids_x4, 4)

    print(f"Combination applied: {combination}")
    print(f"Output: {new_file}")
    return new_file


"""
v = "c17.v"
dir_to_save = "./testes"
combination = ['X1', 'X1', 'X1', 'X1', 'X1', 'X1']
apply_combination(v, dir_to_save, combination, "0_c17.v")
"""

