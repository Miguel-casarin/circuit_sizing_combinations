read_liberty ./data/cells_library/Nangate45_typ.lib
read_verilog ./output/temp/0_b11_C.v
link_design b11_C

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {X_IN_5_ X_IN_4_ X_IN_3_ X_IN_2_ X_IN_1_ X_IN_0_ STBI STATO_REG_0__SCAN_IN STATO_REG_1__SCAN_IN STATO_REG_2__SCAN_IN STATO_REG_3__SCAN_IN X_OUT_REG_0__SCAN_IN X_OUT_REG_1__SCAN_IN X_OUT_REG_2__SCAN_IN X_OUT_REG_3__SCAN_IN X_OUT_REG_4__SCAN_IN X_OUT_REG_5__SCAN_IN CONT1_REG_0__SCAN_IN CONT1_REG_1__SCAN_IN R_IN_REG_5__SCAN_IN R_IN_REG_4__SCAN_IN R_IN_REG_3__SCAN_IN R_IN_REG_2__SCAN_IN R_IN_REG_1__SCAN_IN R_IN_REG_0__SCAN_IN CONT_REG_5__SCAN_IN CONT_REG_4__SCAN_IN CONT_REG_3__SCAN_IN CONT_REG_2__SCAN_IN CONT_REG_1__SCAN_IN CONT_REG_0__SCAN_IN CONT1_REG_8__SCAN_IN CONT1_REG_7__SCAN_IN CONT1_REG_6__SCAN_IN CONT1_REG_5__SCAN_IN CONT1_REG_4__SCAN_IN CONT1_REG_3__SCAN_IN CONT1_REG_2__SCAN_IN}]

set_output_delay 1 -clock virt_clk [get_ports {U404 U405 U406 U407 U408 U409 U384 U383 U382 U381 U380 U379 U378 U377 U376 U375 U374 U373 U372 U371 U370 U369 U368 U367 U366 U365 U364 U360 U361 U362 U363}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 31

exit

