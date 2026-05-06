import os

def get_files(designs_path):

    circuits_list = []
    files = os.listdir(designs_path)

    for file in files:
        circuits_list.append(file)
        print(f"File {file} ad to circuit list")

    return circuits_list
    
