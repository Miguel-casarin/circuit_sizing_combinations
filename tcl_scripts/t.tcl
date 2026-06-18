read_liberty ./data/cells_library/ed_Nangate.lib
read_verilog ./output/temp/0_c499.v
link_design c499

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {N1 N5 N9 N13 N17 N21 N25 N29 N33 N37 N41 N45 N49 N53 N57 N61 N65 N69 N73 N77 N81 N85 N89 N93 N97 N101 N105 N109 N113 N117 N121 N125 N129 N130 N131 N132 N133 N134 N135 N136 N137}]

set_output_delay 1 -clock virt_clk [get_ports {N724 N725 N726 N727 N728 N729 N730 N731 N732 N733 N734 N735 N736 N737 N738 N739 N740 N741 N742 N743 N744 N745 N746 N747 N748 N749 N750 N751 N752 N753 N754 N755}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 32

exit

