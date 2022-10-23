# Tangerine SDR Development Utilities

## This is a developer repository for utilities related to the TangerineSDR FPGA and C code. This version is intended for the MAX10 Development Board, the TAPR DE_Adapter, Receiver Module, and Clock Module.

### This repository will be updated as the amount of functionaly that works grows and more CLI commands are useable.

-------------------------------
The only utility right now is a CLI (Command Line Interface) for talking to the TangerineSDR DevKit over the Gigabit Ethernet Interface. Upon invocation it tries to discover any alive OpenHPSDR system on the local LAN via broadcast/24. It then opens a provisioning channel and accepts a small set of commands that are useful in testing the TangerineSDR DevKit+DE_Adapter+Clock_Module.

This program requires 3 files be located in the same directory:
1. DE_CLI.py
2. DE_Connection.py
3. exceptions.py

Start the program by running DE_CLI.py in a python3 interpreter.
It will import and use the other 2 files. The target system must be reachable on the same LAN.



