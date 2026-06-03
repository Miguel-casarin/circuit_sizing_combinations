read_liberty ./data/cells_library/ed_Nangate.lib
read_verilog ./output/temp/2_teste2.v
link_design teste2

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {N1}]

set_output_delay 1 -clock virt_clk [get_ports {N3}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 1

exit

