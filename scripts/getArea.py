import json

def search_area(cell: str, data_json) -> float:
    with open(data_json, "r") as f:
        areas = json.load(f)
    return areas.get(cell, None)

def get_previous_area(cell: str, data_json: str) -> float:
    size_map = {"X4": "X2", "X2": "X1", "X1": None}
    
    for size, prev_size in size_map.items():
        if cell.endswith(size):
            if prev_size is None:
                return 0.0
            previous_cell = cell.replace(size, prev_size)
            area = search_area(previous_cell, data_json)
            return area if area is not None else 0.0
    
    return 0.0

def cost_area(new_area: float, previos_area: float) -> float:
    return (new_area - previos_area)