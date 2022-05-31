from itertools import product

from aalpy.utils import generate_random_mdp, generate_random_smm

automata_size = [3, 5, 10, 15, 20, 25, 40, 50, 75, 90, 100, 150, 200]
inputs_size = [2, 3, 4, 5, 6, 7, 8, 9, 10]
outputs_size = [2, 4, 6, 8, 10, 15, 20]

for p in product(automata_size, inputs_size, outputs_size):
    num_states, num_inputs, num_outputs = p
    random_mdp = generate_random_mdp(num_states=num_states, input_size=num_inputs, output_size=num_outputs)
    random_smm = generate_random_smm(num_states=num_states, input_size=num_inputs, output_size=num_outputs)

    # TODO