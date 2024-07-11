"""File to import and parse verilog modules"""

from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import Source, ModuleDef
from pyverilog.vparser.ast import Decl, Inout, Input, Output, Reg, Wire
from pyverilog.vparser.ast import Pointer, Lvalue, Rvalue
from pyverilog.vparser.ast import Assign, Partselect, LConcat, Concat
from pyverilog.vparser.ast import InstanceList, Instance
from pyverilog.vparser.ast import Always, BlockingSubstitution, NonblockingSubstitution, Identifier
from pyverilog.vparser.ast import Uand, Ulnot, Uminus, Unand, Unor, Unot, Uor, Uplus, Uxnor, Uxor

from rulebookv2 import gate_function

import json
import sys


# Function to initialise a dictionary to store module data.
def init_empty_module(name: str):
  moduleKeys = [
    "inputs",
    "outputs",
    "inouts",
    "wires",
    "registers",
    "components",
    "assignments",
    "always",
  ]
  newModule = {"name": name} | dict.fromkeys(moduleKeys, [])
  return newModule


# Function to define all the module parameters.
def define_module(moduleDef, newModuleDict):
  if isinstance(moduleDef, ModuleDef):
    items = moduleDef.items
    for i in range(len(items)):
      item = items[i]

      # Declarations
      if isinstance(item, Decl):
        for j in range(len(item.list)):
          category = item.list[j]

          # Inputs
          if isinstance(category, Input):
            newModuleDict["inputs"] = newModuleDict["inputs"] + [{"name": category.name, "width": "1"}]
            if category.width != None:
              lsb = category.width.lsb.value
              msb = category.width.msb.value
              newModuleDict["inputs"][-1]["width"] = str(abs(int(msb) - int(lsb)) + 1)
              newModuleDict["inputs"][-1]["lsb"] = lsb
              newModuleDict["inputs"][-1]["msb"] = msb

          # Outputs
          elif isinstance(category, Output):
            newModuleDict["outputs"] = newModuleDict["outputs"] + [{"name": category.name, "width": "1"}]
            if category.width != None:
              lsb = category.width.lsb.value
              msb = category.width.msb.value
              newModuleDict["outputs"][-1]["width"] = str(abs(int(msb) - int(lsb)) + 1)
              newModuleDict["outputs"][-1]["lsb"] = lsb
              newModuleDict["outputs"][-1]["msb"] = msb

          # Inouts
          elif isinstance(category, Inout):
            newModuleDict["inouts"] = newModuleDict["inouts"] + [{"name": category.name, "width": "1"}]
            if category.width != None:
              lsb = category.width.lsb.value
              msb = category.width.msb.value
              newModuleDict["inouts"][-1]["width"] = str(abs(int(msb) - int(lsb)) + 1)
              newModuleDict["inouts"][-1]["lsb"] = lsb
              newModuleDict["inouts"][-1]["msb"] = msb

          # Registers
          elif isinstance(category, Reg):
            newModuleDict["registers"] = newModuleDict["registers"] + [{"name": category.name, "width": "1"}]
            if category.width != None:
              lsb = category.width.lsb.value
              msb = category.width.msb.value
              newModuleDict["registers"][-1]["width"] = str(abs(int(msb) - int(lsb)) + 1)
              newModuleDict["registers"][-1]["lsb"] = lsb
              newModuleDict["registers"][-1]["msb"] = msb

          # Wires
          elif isinstance(category, Wire):
            newModuleDict["wires"] = newModuleDict["wires"] + [{"name": category.name, "width": "1"}]
            if category.width != None:
              lsb = category.width.lsb.value
              msb = category.width.msb.value
              newModuleDict["wires"][-1]["width"] = str(abs(int(msb) - int(lsb)) + 1)
              newModuleDict["wires"][-1]["lsb"] = lsb
              newModuleDict["wires"][-1]["msb"] = msb

          else:
            print("Error: Invalid declaration type.")

      # Assign Statements
      elif isinstance(item, Assign):
        left = item.left
        right = item.right

        if isinstance(left, Lvalue) & isinstance(right, Rvalue):
          # List, List
          if isinstance(left.var, LConcat) & isinstance(right.var, Concat):
            if (len(left.var.list) == len(right.var.list)):
              for j in range(len(left.var.list)):
                if isinstance(left.var.list[j], Pointer):
                  dest = (left.var.list[j].var.name + "_" + left.var.list[j].ptr.value)
                else:
                  dest = left.var.list[j].name

                if isinstance(right.var.list[j], Pointer):
                  src = (right.var.list[j].var.name + "_" + right.var.list[j].ptr.value)
                else:
                  src = right.var.list[j].name

                newModuleDict["assignments"] = newModuleDict["assignments"] + [
                  {
                    "dest": dest,
                    "src": src,
                  }
                ]

            else:
              print("Error: Mismatch in number of wires concatenated.")

          # List, Wires
          elif isinstance(left.var, LConcat) & isinstance(right.var, Partselect):
            for j in range(len(left.var.list)):
              if isinstance(left.var.list[j], Pointer):
                dest = (left.var.list[j].var.name + "_" + left.var.list[j].ptr.value)
              else:
                dest = left.var.list[j].name

              newModuleDict["assignments"] = newModuleDict["assignments"] + [
                {
                  "dest": dest,
                  "src": right.var.var.name
                  + "_"
                  + str(int(right.var.msb.value) - j),
                }
              ]

          # Wires, List
          elif isinstance(left.var, Partselect) & isinstance(right.var, Concat):
            for j in range(len(right.var.list)):
              if isinstance(right.var.list[j], Pointer):
                src = (right.var.list[j].var.name + "_" + right.var.list[j].ptr.value)
              else:
                src = right.var.list[j].name

              newModuleDict["assignments"] = newModuleDict["assignments"] + [
                {
                  "dest": left.var.var.name
                  + "_"
                  + str(int(left.var.msb.value) - j),
                  "src": src,
                }
              ]

          # Otherwise
          else:
            newModuleDict["assignments"] = newModuleDict["assignments"] + [
              {"dest": left.var.name, "src": right.var.name}
            ]

        else:
          print("Error: Invalid assign parameters.")

      # Gates and Sub-modules
      elif isinstance(item, InstanceList):
        for j in range(len(item.instances)):
          instance = item.instances[j]

          if isinstance(instance, Instance):
            newModuleDict["components"] = newModuleDict["components"] + [
              {
                "name": instance.name,
                "module": instance.module,
                "ports": [],
              }
            ]

            # Basic Gates
            if ((instance.module == "not")
              | (instance.module == "and")
              | (instance.module == "or")
              | (instance.module == "nand")
              | (instance.module == "nor")
              | (instance.module == "xor")
              | (instance.module == "xnor")
            ):
              for k in range(len(instance.portlist)):
                if isinstance(instance.portlist[k].argname, Pointer):
                  argname = (instance.portlist[k].argname.var.name + "_" + instance.portlist[k].argname.ptr.value)
                else:
                  argname = instance.portlist[k].argname.name

                if k == 0:
                  newModuleDict["components"][-1]["ports"] = newModuleDict["components"][-1]["ports"] + [
                    {
                      "portname": "out",
                      "argname": argname,
                    }
                  ]
                else:
                  newModuleDict["components"][-1]["ports"] = newModuleDict["components"][-1]["ports"] + [
                    {
                      "portname": "in" + str(k - 1),
                      "argname": argname,
                    }
                  ]

            # Custom Sub-modules
            else:
              for k in range(len(instance.portlist)):
                if isinstance(instance.portlist[k].argname, Pointer):
                  argname = (instance.portlist[k].argname.var.name + "_" + instance.portlist[k].argname.ptr.value)
                else:
                  argname = instance.portlist[k].argname.name

                newModuleDict["components"][-1]["ports"] = newModuleDict["components"][-1]["ports"] + [
                  {
                    "portname": instance.portlist[k].portname,
                    "argname": argname,
                  }
                ]

          else:
            print("Error: Invalid instance.")

      # Always Blocks
      elif isinstance(item, Always):
        newModuleDict["always"] = newModuleDict["always"] + [{"dependencies": [], "statements": []}]

        # Dependencies
        for j in range(len(item.sens_list.list)):
          dependency = item.sens_list.list[j]
          newModuleDict["always"][-1]["dependencies"].append({"signal": dependency.sig.name, "type": dependency.type})

        # Statements
        for j in range(len(item.statement.statements)):
          statement = item.statement.statements[j]
          if isinstance(statement, (BlockingSubstitution, NonblockingSubstitution)):
            # Element
            if isinstance(statement.left.var, Identifier):
              dest = statement.left.var.name
            # Sub-element
            elif isinstance(statement.left.var, Pointer):
              dest = statement.left.var.name + "_" + statement.left.ptr.value
            else:
              print("Error: Invalid instance type.")
              continue

            # Element
            if isinstance(statement.right.var, Identifier):
              src = statement.right.var.name
            # Sub-element
            elif isinstance(statement.right.var, Pointer):
              src = statement.right.var.name + "_" + statement.right.ptr.value
            # Unary operation
            elif isinstance(statement.right.var, (Uand, Ulnot, Uminus, Unand, Unor, Unot, Uor, Uplus, Uxnor, Uxor)):
              # Element
              if isinstance(statement.right.var, Identifier):
                src = {
                  "unaryop": str(statement.right.var.__class__.__name__),
                  "identifier": statement.right.var.right.name,
                }
              # Sub-element
              elif isinstance(statement.right.var, Pointer):
                src = {
                  "unaryop": str(statement.right.var.__class__.__name__),
                  "identifier": statement.right.var.right.var.name + "_" + statement.right.var.right.ptr.value,
                }
            else:
              print("Error: Invalid instance type.")
              continue

            newModuleDict["always"][-1]["statements"].append(
              {
                "dest": dest,
                "src": src,
              }
            )

            # Pre-delay
            if statement.ldelay != None:
              predelay = statement.ldelay.delay.value
              newModuleDict["always"][-1]["statements"][-1]["predelay"] = predelay

            # Post-delay
            if statement.rdelay != None:
              postdelay = statement.rdelay.delay.value
              newModuleDict["always"][-1]["statements"][-1]["postdelay"] = postdelay

          else:
            print("Error: Invalid statement.")

      else:
        print("Error: Invalid item.")

  else:
    print("Error: Invalid moduleDef type.")


# Function to add module to the circuit tree.
def add_module(tree, moduleDef):
  if isinstance(moduleDef, ModuleDef):
    if moduleDef.name not in tree["modules"]:
      # Create new module dictionary.
      newModuleDict = init_empty_module(moduleDef.name)
      define_module(moduleDef, newModuleDict)
      # Add module to tree.
      tree["modules"] = tree["modules"] | {moduleDef.name: newModuleDict}

  else:
    print("Error: Invalid moduleDef type.")


# Function to initialise primary input with its fault list.
def input_fault_list(wire_name, wire_logic):
  fault_list = set()
  if wire_logic == 0:
    fault_list.add(f"{wire_name}/1")
  else:
    fault_list.add(f"{wire_name}/0")
  return list(fault_list)


# Function to create test vector data and initialise primary input fault list.
def init_test_vector(tree, test, wrapper_name):
  # Check if length of test vector is the same as number of inputs.
  if (len(test) == len(tree["modules"][wrapper_name]["inputs"])):
    # Create test vector and corresponding input.
    test_vector = {}
    for j in range(len(tree["modules"][wrapper_name]["inputs"])):
      input = tree["modules"][wrapper_name]["inputs"][j]
      # If input is other than 0 and 1.
      if ((test[j] != "1") and (test[j] != "0")):
        print("Invalid input in test vector", test, "\nInputs can only be either 0 or 1. Test vector ignored.")
        return
      test_vector[input["name"]] = int(test[j])
    # Add test vector to list of tests.
    tree["wrapper"]["test_vectors"] = tree["wrapper"]["test_vectors"] + [test]
    tree["wrapper"]["wire_logic_values"][test] = test_vector

    # Create a dict for the test vector in results.
    fault_lists = {}
    for input in tree["modules"][wrapper_name]["inputs"]:
      fault_lists[input["name"]] = input_fault_list(input["name"], test_vector[input["name"]])
    tree["wrapper"]["wire_fault_lists"][test] = fault_lists
    return

  # Print error if lengths don't match.
  else:
    print("Invalid length for test vector", test, "\nTest vector ignored.")
    return


# Function to create a decision tree.
def create_decision_tree(ast, wrapper_name: str, test_list: list):
  if isinstance(ast, Source):
    treeKeys = ["modules", "components", "wrapper"]
    tree = dict.fromkeys(treeKeys, {})
    for i in range(len(ast.description.definitions)):
      add_module(tree, ast.description.definitions[i])

    if wrapper_name in tree["modules"]:
      # Initialise wrapper component.
      tree["wrapper"] = { "module_name": wrapper_name, "test_vectors": [], "wire_logic_values": {}, "wire_fault_lists": {}}
      # Parse test vectors.
      for i in range(len(test_list)):
        test: str = test_list[i]
        init_test_vector(tree, test, wrapper_name)

    else:
      print("Error: Invalid wrapper module name.")
      return None

    return tree

  else:
    print("Error: Invalid AST.")
    return None


# Function to generate fault list for a gate.
def make_fault_list(tree, test_vector, component):
  logic_values = tree["wrapper"]["wire_logic_values"][test_vector]
  fault_lists = tree["wrapper"]["wire_fault_lists"][test_vector]

  # Inputs to be passed for deductive fault list generation.
  gate = component["module"]
  input_names = []
  input_logics = []
  input_fault_list = []
  for port in component["ports"]:
    # output
    if (port["portname"] == "out"):
      output = port["argname"]
    # input
    else:
      input_names = input_names + [port["argname"]]
      input_logics = input_logics + [logic_values[port["argname"]]]
      input_fault_list = input_fault_list + [fault_lists[port["argname"]]]
  
  # Find the fault list for the output of the gate.
  output_fault_simulation = gate_function(gate, input_names, input_logics, input_fault_list, output)

  # Add output fault list and value to the wrapper.
  tree["wrapper"]["wire_logic_values"][test_vector] = tree["wrapper"]["wire_logic_values"][test_vector] | {output: output_fault_simulation["output_logic"]}
  tree["wrapper"]["wire_fault_lists"][test_vector] = tree["wrapper"]["wire_fault_lists"][test_vector] | {output: output_fault_simulation["fault_list"]}

  return
  

# Function to traverse the decision tree and generate fault lists.
def traverse_decision_tree(tree, wrapper, vector):
  for component in tree["modules"][wrapper]["components"]:
    # Basic Gates.
    if ((component["module"] == "not")
      | (component["module"] == "and")
      | (component["module"] == "or")
      | (component["module"] == "nand")
      | (component["module"] == "nor")
      | (component["module"] == "xor")
      | (component["module"] == "xnor")
    ):
      make_fault_list(tree, vector, component)

  return


# Function to perform deductivve fault simulation and return the decision tree.
def deductive_fault_simulation(ckt_file, tests, wrapper):
  # Parse the Verilog file
  ast, directives = parse(ckt_file)
  # Generate the decision tree.
  tree = create_decision_tree(ast, wrapper, tests)
  # Perform fault simulation for each test vector input.
  for test in tree["wrapper"]["test_vectors"]:
    traverse_decision_tree(tree, wrapper, test)
    
    # Generate final list of faults.
    final_fault_list = set()
    for output in tree["modules"][wrapper]["outputs"]:
      final_fault_list.update(set(tree["wrapper"]["wire_fault_lists"][test][output["name"]]))
    
    # Print final fault list.
    print("Test Vector:", test)
    print("List of faults detected at the output:", list(final_fault_list))

  return tree

# Command format: python .\verilogParser.py .\benchmark.v benchmark 1 000000 output_benchmark.json

# Verilog circuit file.
ckt = open(sys.argv[1])
# Name of wrapper module.
wrapper = sys.argv[2]
# Number of test vectors.
test_count = sys.argv[3]
# List of test vectors.
tests = []
for i in range(int(test_count)):
  tests.append(sys.argv[4 + i])

# # For debugging benchmark.
# # Verilog circuit file.
# ckt = open("benchmark.v")
# # Name of wrapper module.
# wrapper = "benchmark"
# # Number of test vectors.
# test_count = 1
# # List of test vectors.
# tests = ["000000"]

# # For debugging c17.
# # Verilog circuit file.
# ckt = open("c17.v")
# # Name of wrapper module.
# wrapper = "c17"
# # Number of test vectors.
# test_count = 1
# # List of test vectors.
# tests = ["00000"]

# Perform Deductive Fault Simulation and store decision tree.
decision_tree = deductive_fault_simulation(ckt, tests, wrapper)

# Storing the output as a JSON file.
with open(sys.argv[-1], "w") as json_output_fp:
  json.dump(decision_tree, json_output_fp)
