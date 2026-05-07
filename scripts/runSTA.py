import re
import subprocess
import os

def rename(string):
    id = re.match(r'^(.*)\.v$', string)

    if id:
        return id.group(1)

def open_sta(tcl_script, n_save, out_dir):
    n_save = f"{n_save}.txt"
    output_path = os.path.join(out_dir, n_save)

    with open(output_path, "w") as f:
          subprocess.run(
            ["sta", tcl_script],
            stdout=f,
            stderr=subprocess.STDOUT,  # STDOUT serve para mostrar os erros
            text=True
        )
          
