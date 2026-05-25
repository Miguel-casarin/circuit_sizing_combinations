# Data Analysis of Delay, Area, and Power in Circuit Netlists

This project analyzes size combinations for gates in a circuit using the NanGate45 cell library. It evaluates how different sizing choices affect delay, area, and power by exploring possible transitions among cell sizes (X1, X2, X4).

## OpenSTA use case
We use OpenSTA (from the OpenROAD project) to extract timing information such as arrival times, power, area, and critical-path cells. OpenSTA is automated via Python's subprocess module to run the static timing analysis and collect results.

## Gate features
Gate features (fan-in, fan-out, logic depth, and logic level) are extracted with NajaEDA to help characterize gates and guide sizing decisions.

## Cells library and supported circuits
This tool is designed to work with the NanGate45 standard cell library and ISCAS85 benchmarks in Verilog. Verilog files and generated sized netlists are stored under data/verilogs and data/verilogs_base.

## Project layout (brief)
- data/verilogs/        — generated/verilog sized netlists
- data/verilogs_base/   — base Verilog files
- output/               — results from STA, tables and transitions
- scripts/              — helpers: STA parsing, encoders, file utilities, etc.

## Notes
- Combinations use sizes X1, X2, X4.
- Make sure OpenSTA and any required tools are installed and reachable from your PATH.
- If you change the naming (e.g., lowercase vs uppercase sizes), keep it consistent across scripts and data files.

## TECHNOLOGIES USED
[STA](https://github.com/The-OpenROAD-Project/OpenSTA)
[NanGate](https://github.com/ABKGroup/NanGate45-Synopsys-Enablement)
[ISCAS85](https://github.com/santoshsmalagi/Benchmarks)
[NajaEDA](https://najaeda.readthedocs.io/en/latest/introduction.html)

## Research Context
This project was developed as part of a research activity at the Federal University of Rio Grande (FURG), under the guidance and supervision of professors Rafael B. Schittz, Paulo F. Butzen and collaboration of research colleague Marcelo F. Donigno.