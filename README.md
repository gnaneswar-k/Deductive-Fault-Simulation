# Deductive Fault Simulation

Design For Testability (Spring 2023) Course Project

## Features

- Parse a circuit defined in Verilog and generate a decision tree containing the details of the circuit and the test vectors.
- Preliminary error checking for any faults in the circuit declaration such as re-declaration of modules.
- Detect faulty test vectors such as when the test vector length does not match the number of inputs of the circuit, or if the test vector contains values other than 0 and 1.
- Perform deductive fault simulation on the circuit, including support for gates with multiple inputs, and generate fault lists for all the wires for all valid test vectors.
- Generate a JSON file containing the decision tree and fault lists.

## Constraints

- The Verilog file cannot contain sub-modules.
- The circuit needs to be defined as per the gate levels, i.e. gates should be defined from highest to lowest proximity to the primary inputs.
- Each wire and gate should have a unique name.
- Input test vectors must be binary (base 2), i.e. they cannot be given as decimal (base 10), hexadecimal (base 16), etc.
