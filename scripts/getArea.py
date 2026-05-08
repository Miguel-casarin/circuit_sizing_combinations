import json

def search_area(cell: str, data_json) -> float:
    with open(data_json, "r") as f:
        areas = json.load(f)
    return areas.get(cell, None)

def cost_area(new_area: float, previos_area: float) -> float:
    return (new_area - previos_area)