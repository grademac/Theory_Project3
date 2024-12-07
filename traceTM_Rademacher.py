import csv

class TuringMachine:
    def __init__(self, name, states, alphabet, transitions, start_state, accept_state, reject_state):
        #define turing machine
        self.name = name
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  
        self.start_state = start_state
        self.accept_state = accept_state
        self.reject_state = reject_state

    def trace_path(self, input_string, max_depth, output_file):
        with open(output_file, "w") as file:
            file.write(f"Machine: {self.name}\n")
            file.write(f"Initial string: {input_string}\n")
            file.write(f"Max depth: {max_depth}\n")

            # Initialize configuration tree
            tree = [[("", self.start_state, input_string)]]
            total_trans = 0
            total_nonleaves = 1

            parent_map = {("", self.start_state, input_string): None}

            for depth in range(max_depth):
                current_level = tree[-1]
                next_level = []
                total_trans += len(current_level)

                for config in current_level:
                    left_tape, state, right_tape = config

                    # If state is accept or reject, no further transitions
                    if state == self.accept_state:
                        file.write(f"String accepted in {depth} transitions\n")
                        self.print_path(file, parent_map, config)
                        file.write(f"Number of configurations explored: {total_nonleaves}\n")
                        self.print_nondeterminism(total_nonleaves, total_trans, file)
                        return
                    if state == self.reject_state:
                        next_level.append(config)
                        continue

                    # Get the current tape symbol (use blank if tape is empty)
                    current_symbol = right_tape[0] if right_tape else "_"

                    # Check for transitions
                    if (state, current_symbol) in self.transitions:
                        has_children = False
                        for new_state, write_symbol, direction in self.transitions[(state, current_symbol)]:
                            has_children = True
                            # Construct new configuration
                            new_left_tape = left_tape
                            new_right_tape = right_tape

                            # Write the symbol
                            if right_tape:
                                new_right_tape = write_symbol + right_tape[1:]
                            else:
                                new_right_tape = write_symbol

                            # Move the tape head
                            if direction == "L":  # Left
                                if new_left_tape:
                                    new_right_tape = new_left_tape[-1] + new_right_tape
                                    new_left_tape = new_left_tape[:-1]
                                else:
                                    new_right_tape = "_" + new_right_tape
                            elif direction == "R":  # Right
                                if new_right_tape:
                                    new_left_tape += new_right_tape[0]
                                    new_right_tape = new_right_tape[1:]
                                else:
                                    new_left_tape += "_"

                            new_config = (new_left_tape, new_state, new_right_tape)
                            if new_config not in parent_map:  # Avoid duplicate entries
                                parent_map[new_config] = config
                                next_level.append(new_config)

                        if has_children:
                            total_nonleaves += 1

                tree.append(next_level)

                # Stop if all configurations lead to reject
                if all(config[1] == self.reject_state for config in next_level):
                    file.write(f"String rejected in {depth + 1} transitions\n")
                    file.write(f"Number of configurations explored: {total_nonleaves}\n")
                    self.print_nondeterminism(total_nonleaves, total_trans, file)
                    return

            file.write(f"Execution stopped after {max_depth} steps\n")
            file.write(f"Total transitions traversed: {total_trans}\n")

    def print_path(self, file, parent_map, final_config):
            #rewrite final accepting path
            path = []
            current = final_config
            while current is not None:
                path.append(current)
                current = parent_map[current]
            path.reverse()
            
            file.write("Accepting path:\n")
            for config in path:
                left_tape, state, right_tape = config
                current_symbol = right_tape[0] if right_tape else "_"
                file.write(f"{left_tape}, {state}, {current_symbol}, {right_tape[1:]}\n")
    
    def print_nondeterminism(self, total_nonleaves, total_trans, file): 
            # Compute the degree of nondeterminism
            if total_nonleaves > 0:
                degree = total_trans / total_nonleaves
            else:
                degree = 0
            file.write(f"Degree of nondeterminism: {degree:.2f}\n")


def parse_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Extract csv data
    name = rows[0][0]
    states = set(rows[1][0:])
    alphabet = set(rows[2][0:])
    start_state = rows[4][0]
    accept_state = rows[5][0]
    reject_state = rows[6][0]

    # Extract transitions
    transitions = {}
    for row in rows[7:]:
        state, symbol, new_state, write_symbol, direction = row
        if (state, symbol) not in transitions:
            transitions[(state, symbol)] = []
        transitions[(state, symbol)].append((new_state, write_symbol, direction))

    return TuringMachine(name, states, alphabet, transitions, start_state, accept_state, reject_state)

#Output

# Load Turing Machine from a CSV file
tm = parse_csv("abc_star_DTM_Rademacher.csv")

# Input string
input_string = "aaabccc"

#output file
output_file = 'output.txt'

max_depth = 20

tm.trace_path(input_string, max_depth, output_file)
