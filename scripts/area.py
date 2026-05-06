import json

def search_area(cell: str, data="areas.json"):
    with open(data, "r") as f:
        areas = json.load(f)
    return areas.get(cell, None)

