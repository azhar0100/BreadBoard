Breadboard
===

This is a project that was made to satisfy an intellectual curiosity. In my university, when we study the subject of DLD, Digital Logic Design, we have to perform lab tasks in which we put together circuits using 747 ICs and breadboards. When using regular wire on a breadboard, the whole circuit can easily become very messy as the wires get tangled. This project aims to solve the problem of "Clean Breadboard Circuit Design". Even though there is very less practical usage for this outside the lab, as breadboards aren't as widely used, and PCB design software are available more widely.

![Messy Breadboard](messywires.JPG?raw=True)

**Disclaimer:** This project is not complete, and the code uploaded is also a fraction of the original code.

Verilog circuit representation
----
In most of our lab tasks, we are given (or else, have to prepare) a verilog representation of the circuit. This representation can be read by a python program using the pyverilog library. First, that representation is used to get a graph representation of the input circuit.
Hence the input is in verilog form.
