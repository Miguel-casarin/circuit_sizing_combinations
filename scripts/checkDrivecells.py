import readV

file = "0_c3.v"
path = "../output/graph/c3"

d = readV.Find_Drive_cells(file, path)
c = d.parse_drives()

print(c)
