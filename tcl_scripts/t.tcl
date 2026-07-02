read_liberty ./data/cells_library/ed_Nangate.lib
read_verilog ./output/temp/0_c1908.v
link_design c1908

create_clock -name virt_clk -period 1.1
#set_load 1.140290 [all_inputs]
set_driving_cell -lib_cell BUF_X4 [all_inputs]
set_load 1.140290 [all_outputs]

set_input_delay 0 -clock virt_clk [get_ports {N1 N4 N7 N10 N13 N16 N19 N22 N25 N28 N31 N34 N37 N40 N43 N46 N49 N53 N56 N60 N63 N66 N69 N72 N76 N79 N82 N85 N88 N91 N94 N99 N104}]

set_output_delay 1 -clock virt_clk [get_ports {N2753 N2754 N2755 N2756 N2762 N2767 N2768 N2779 N2780 N2781 N2782 N2783 N2784 N2785 N2786 N2787 N2811 N2886 N2887 N2888 N2889 N2890 N2891 N2892 N2899}]

# Power 
set_power_activity -input -activity 0.1
report_power

report_checks -digits 5 -path_delay max -group_count 1

exit

