# Deductive Fault Simulation

This repository contains a Python script (`deductive.py`) for parsing a Verilog circuit and generating fault lists for each test vector. Follow the instructions below to run the parser:

## Usage

1. Ensure you have Python installed on your system.
2. Ensure PyVerilog library is installed on your system.
3. Open a terminal and run the following command:

```bash
python deductive.py circuit.v wrapper_module n vector1 vector2 ... vectorN output.json
```

Where

1. `circuit.v`: Verilog fine in which circuit is defined.
2. `wrapper_module`: Name of wrapper module.
3. `n`: Number of test vectors.
4. `vector1 vector2 ... vectorN` *n* test vector inputs. Ensure that inputs are given in the corresponding order as the inputs are declared in the Verilog circuit file.
5. `output.json`: JSON file name which stores the decision tree and fault lists.