import pickle
from collections import defaultdict
from random import seed
from statistics import mean

from aalpy.SULs import DfaSUL, MealySUL
from aalpy.learning_algs import run_Lstar
from aalpy.oracles import StatePrefixEqOracle, RandomWMethodEqOracle
from aalpy.utils import generate_random_deterministic_automata

closing_strategies = ['shortest_first', 'longest_first', 'single', 'single_longest']
closing_strategies = ['shortest_first']

obs_table_cell_prefixes = [True, False]
closedness_types = ['suffix_single', 'suffix_all', ]
cex_processing = [None, 'longest_prefix', 'rs']

automata_size = [1000 ]
input_sizes = [2, 3]
output_sizes = [3, ]
num_repeats = 1

test_models = []
for size in automata_size:
    for i in input_sizes:
        for o in output_sizes:
            random_model = generate_random_deterministic_automata('dfa', size, i, o, num_accepting_states=100)
            test_models.append(random_model)

tc = 0
num_exp = len(test_models) * len(closing_strategies) * len(closedness_types) * num_repeats * len(cex_processing) * len(obs_table_cell_prefixes)
stats = defaultdict(list)
for test_model in test_models:
    input_al = test_model.get_input_alphabet()
    for closedness_type in closedness_types:
        for closing_strategy in closing_strategies:
            for cex in cex_processing:
                for prefix_in_cell in obs_table_cell_prefixes:
                    for _ in range(num_repeats):
                        tc += 1
                        print(round(tc / num_exp * 100, 2))
                        # seed(tc)
                        sul = MealySUL(test_model)
                        eq_oracle = RandomWMethodEqOracle(input_al, sul, walks_per_state=10, walk_len=15)
                        model, info = run_Lstar(input_al, sul, eq_oracle, 'mealy',
                                                closing_strategy=closing_strategy,
                                                cex_processing=cex,
                                                e_set_suffix_closed=True,
                                                all_prefixes_in_obs_table=prefix_in_cell,
                                                print_level=0,
                                                return_data=True)

                        config_name = f'E_set_type_{closedness_type}_closing_strategy_{closing_strategy}' \
                                      f'_cex_{cex}_prefixes_{prefix_in_cell}'
                        stats[config_name].append(
                            (info['queries_learning'],
                             info['steps_learning'],
                             model.size == test_model.size))

with open('stats.pickle', 'wb') as handle:
    pickle.dump(stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('stats.pickle', 'rb') as handle:
#     stats = pickle.load(handle)

statistics_sorted = []
for k, v in stats.items():
    mean_queries, mean_steps, num_correct = mean([x[0] for x in v]), mean([x[1] for x in v]), sum([x[2] for x in v])
    statistics_sorted.append((k, mean_queries, mean_steps, num_correct))

statistics_sorted.sort(key=lambda x: x[2])

for k, q, s, c in statistics_sorted:
    print(k, int(q), int(s), c)
