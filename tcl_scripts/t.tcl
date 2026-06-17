read_liberty ./data/cells_library/ed_Nangate.lib
read_verilog ./output/temp/0_c432.v
link_design c432

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {N1 N4 N8 N11 N14 N17 N21 N24 N27 N30 N34 N37 N40 N43 N47 N50 N53 N56 N60 N63 N66 N69 N73 N76 N79 N82 N86 N89 N92 N95 N99 N102 N105 N108 N112 N115}]

set_output_delay 1 -clock virt_clk [get_ports {N223 N329 N370 N421 N430 N431 N432}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 7

exit

