def gate_function(gate_type, input_names, input_logics, input_faults, output_wire):
    num_inputs = len(input_names)
    output_fault_list = set()

    if gate_type == "and":
        output_logic = all(input_logics)
        output_fault_list = set.union(*(set(fault_list) for fault_list in input_faults))
        if all(logic == 1 for logic in input_logics):
            output_fault_list.add(f"{output_wire}/0")
        else:
            for i in range(num_inputs):
                if input_logics[i] == 0:
                    output_fault_list.intersection_update(input_faults[i])
                else:
                    output_fault_list.difference_update(input_faults[i])
            output_fault_list.add(f"{output_wire}/1")

    elif gate_type == "or":
        output_logic = any(input_logics)
        output_fault_list = set.union(*(set(fault_list) for fault_list in input_faults))
        if all(logic == 0 for logic in input_logics):
            output_fault_list.add(f"{output_wire}/1")
        else:
            for i in range(num_inputs):
                if input_logics[i] == 1:
                    output_fault_list.intersection_update(input_faults[i])
                else:
                    output_fault_list.difference_update(input_faults[i])
            output_fault_list.add(f"{output_wire}/0")

    elif gate_type == "nand":
        output_logic = not all(input_logics)
        output_fault_list = set.union(*(set(fault_list) for fault_list in input_faults))
        if all(logic == 1 for logic in input_logics):
            output_fault_list.add(f"{output_wire}/1")
        else:
            for i in range(num_inputs):
                if input_logics[i] == 0:
                    output_fault_list.intersection_update(input_faults[i])
                else:
                    output_fault_list.difference_update(input_faults[i])
            output_fault_list.add(f"{output_wire}/0 ")

    elif gate_type == "nor":
        output_logic = not any(input_logics)
        output_fault_list = set.union(*(set(fault_list) for fault_list in input_faults))
        if all(logic == 0 for logic in input_logics):
            output_fault_list.add(f"{output_wire}/0")
        else:
            for i in range(num_inputs):
                if input_logics[i] == 1:
                    output_fault_list.intersection_update(input_faults[i])
                else:
                    output_fault_list.difference_update(input_faults[i])
            output_fault_list.add(f"{output_wire}/1")

    elif gate_type == "not":
        output_logic = not input_logics[0]
        output_fault_list = set.union(*(set(fault_list) for fault_list in input_faults))
        if input_logics[0] == 0:
            output_fault_list.add(f"{output_wire}/0")
        else:
            output_fault_list.add(f"{output_wire}/1")

    elif gate_type == "xor":
        output_logic = sum(input_logics) % 2
        output_fault_list = set.union(*(set(fault_list) for fault_list in input_faults))
        num_inputs = len(input_names)
            
        if output_logic == 0:
            output_fault_list.add(f"{output_wire}/1")
        else:
            output_fault_list.add(f"{output_wire}/0")
            
        # Make a list with the frequency of faults for input logic 1 and 0
        logic_1_faults = [fault for i in range(num_inputs) if input_logics[i] == 1 for fault in input_faults[i]]
        logic_0_faults = [fault for i in range(num_inputs) if input_logics[i] == 0 for fault in input_faults[i]]

        # Count the frequency of each fault in the lists
        logic_1_fault_counts = {fault: logic_1_faults.count(fault) for fault in set(logic_1_faults)}
        logic_0_fault_counts = {fault: logic_0_faults.count(fault) for fault in set(logic_0_faults)}

        # Remove faults with even frequency from the union list
        for fault, count in logic_1_fault_counts.items():
            if count % 2 == 0:
                output_fault_list.discard(fault)

        for fault, count in logic_0_fault_counts.items():
            if count % 2 == 0:
                output_fault_list.discard(fault)
        
    return {"output_logic": int(output_logic), "fault_list": list(output_fault_list)}