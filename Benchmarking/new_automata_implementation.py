import time

from aalpy.utils import generate_random_deterministic_automata
from random import randint, choice

model = generate_random_deterministic_automata('mealy', num_states=100, input_alphabet_size=4, output_alphabet_size=2)
input_al = model.get_input_alphabet()

time_old, time_new = 0, 0


class NewMealy:
    def __init__(self, state_dict):
        self.state_dict = state_dict
        self.initial_state = 's1'
        self.current_state = self.initial_state

    def step(self, x):
        output, self.current_state = self.state_dict[self.current_state][x]
        return output

    def execute_sequence(self, initial_state, seq):
        self.initial_state = initial_state
        return [self.step(x) for x in seq]

new_model = NewMealy(model.to_state_setup())

test_set = []
for _ in range(1000000):
    test_set.append([choice(input_al) for _ in range(randint(3, 10))])

start = time.time()
for t in test_set:
    model.execute_sequence(model.initial_state, t)
time_old = time.time() - start

start = time.time()
for t in test_set:
    new_model.execute_sequence(model.initial_state, t)
time_new = time.time() - start

print('time old', time_old)
print('time new', time_new)