class Netlist_and_path:

    def __init__(self):
        self.nets_and_path = {}

    def add_values(self, key) -> None:
        self.nets_and_path[key] = {
            "LOGIC-TYPE": str,
            "PATH-OCURENCE": int,
            "FA-IN": int,
            "FA-OUT": int,
            "LOGIC-LEVEL": int,
            "DEEP": int,
        }

class Manipulet_dict(Netlist_and_path):

    def __init__(self):
        super().__init__()

    def popular_dictionary(self, cells_id_list, logic_type_list):
        for key, logic_type in zip(cells_id_list, logic_type_list):
            self.add_values(key)
            self.nets_and_path[key]["LOGIC-TYPE"] = logic_type

    def ad_fanout(self, key, fanout):
        self.nets_and_path[key]["FA-OUT"] = fanout

    def ad_logic_level(self, key, level):
        self.nets_and_path[key]["LOGIC-LEVEL"] = level

    def ad_deep(self, key, deep):
        self.nets_and_path[key]["DEEP"] = deep

    def ad_path_occurrence(self, key, occurrence):
        self.nets_and_path[key]["PATH-OCURENCE"] = occurrence
