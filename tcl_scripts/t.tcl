read_liberty ./data/cells_library/Nangate45_typ.lib
read_verilog ./output/temp/0_c880.v
link_design c880

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {N1 N8 N13 N17 N26 N29 N36 N42 N51 N55 N59 N68 N72 N73 N74 N75 N80 N85 N86 N87 N88 N89 N90 N91 N96 N101 N106 N111 N116 N121 N126 N130 N135 N138 N143 N146 N149 N152 N153 N156 N159 N165 N171 N177 N183 N189 N195 N201 N207 N210 N219 N228 N237 N246 N255 N259 N260 N261 N267 N268}]

set_output_delay 1 -clock virt_clk [get_ports {N388 N389 N390 N391 N418 N419 N420 N421 N422 N423 N446 N447 N448 N449 N450 N767 N768 N850 N863 N864 N865 N866 N874 N878 N879 N880}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 26

exit

