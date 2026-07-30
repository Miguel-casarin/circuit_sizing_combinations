read_liberty ./data/cells_library/Nangate45_typ.lib
read_verilog ./output/temp/0_b01_C.v
link_design b01_C

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {LINE1 LINE2 STATO_REG_2__SCAN_IN STATO_REG_1__SCAN_IN STATO_REG_0__SCAN_IN}]

set_output_delay 1 -clock virt_clk [get_ports {U45 U36 U35 U44 U34}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 5

exit

