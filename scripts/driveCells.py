import json

def return_drive_cells(cell_name: str, json_path) -> list:
    with open(json_path, "r") as f:
        data = json.load(f)

    sizes = []

    for key in data.keys():
        if key.startswith(cell_name + "_"):
            size = key.split("_")[-1]
            sizes.append(size)

    return sizes

