read_liberty ./data/cells_library/ed_Nangate.lib
read_verilog ./output/temp/0_c3540.v
link_design c3540

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {N1 N13 N20 N33 N41 N45 N50 N58 N68 N77 N87 N97 N107 N116 N124 N125 N128 N132 N137 N143 N150 N159 N169 N179 N190 N200 N213 N222 N223 N226 N232 N238 N244 N250 N257 N264 N270 N274 N283 N294 N303 N311 N317 N322 N326 N329 N330 N343 N349 N350}]

set_output_delay 1 -clock virt_clk [get_ports {N1713 N1947 N3195 N3833 N3987 N4028 N4145 N4589 N4667 N4815 N4944 N5002 N5045 N5047 N5078 N5102 N5120 N5121 N5192 N5231 N5360 N5361}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 22

exit

