import pickle
from collections import defaultdict
from random import seed
from statistics import mean

from aalpy.SULs import DfaSUL, MealySUL
from aalpy.learning_algs import run_Lstar
from aalpy.oracles import StatePrefixEqOracle, RandomWMethodEqOracle
from aalpy.utils import generate_random_deterministic_automata

is_suffix_closed = [True, False]
closedness_types = ['suffix', 'prefix']
closing_strategies = ['shortest_first', 'longest_first', 'single', 'single_longest']
cex_processing = ['rs', 'longest_prefix']

automata_size = [500, 1000,]
input_sizes = [2, 4, 6,]
output_sizes = [2, 3, 4]

test_models = []
for size in automata_size:
    for i in input_sizes:
        for o in output_sizes:
            random_model = generate_random_deterministic_automata('mealy', size, i, o)
            test_models.append(random_model)

tc = 0
num_exp = len(test_models) * len(is_suffix_closed) * len(closing_strategies) * len(closedness_types)
stats = defaultdict(list)
for test_model in test_models:
    input_al  = test_model.get_input_alphabet()

    for suffix_closedness_type in is_suffix_closed:
        for closedness_type in closedness_types:
            for closing_strategy in closing_strategies:
                tc+=1
                print(round(tc/num_exp * 100,2))
                seed(tc)
                sul = MealySUL(test_model)
                eq_oracle = RandomWMethodEqOracle(input_al, sul, walks_per_state=10, walk_len=10)
                model, info = run_Lstar(input_al, sul, eq_oracle, 'mealy',
                                        suffix_closedness=suffix_closedness_type,
                                        closedness_type=closedness_type,
                                        closing_strategy=closing_strategy,
                                        print_level=1,
                                        return_data=True)

                config_name = f'closed_{suffix_closedness_type}_closing_type_{closedness_type}_closing_strategy_{closing_strategy}'
                stats[config_name].append((info['queries_learning'], info['steps_learning']))

with open('stats.pickle', 'wb') as handle:
    pickle.dump(stats, handle, protocol=pickle.HIGHEST_PROTOCOL)

# with open('stats.pickle', 'rb') as handle:
#     stats = pickle.load(handle)

statistics_sorted = []
for k, v in stats.items():
    mean_queries, mean_steps = mean([x[0] for x in v]), mean([x[1] for x in v])
    statistics_sorted.append((k, mean_queries, mean_steps))

statistics_sorted.sort(key=lambda x:x[1])

for k, q, s in statistics_sorted:
    print(k, int(q), int(s))

# closed_True_closing_type_prefix_closing_strategy_single 37536 305788
# closed_True_closing_type_prefix_closing_strategy_longest_first 38656 330579
# closed_True_closing_type_prefix_closing_strategy_shortest_first 39021 315446
# closed_True_closing_type_prefix_closing_strategy_single_longest 39116 2365613
# closed_True_closing_type_suffix_closing_strategy_single_longest 43312 2527777
# closed_False_closing_type_prefix_closing_strategy_shortest_first 44462 367800
# closed_True_closing_type_suffix_closing_strategy_single 44535 359985
# closed_False_closing_type_suffix_closing_strategy_longest_first 44633 383416
# closed_False_closing_type_prefix_closing_strategy_single 45051 370958
# closed_False_closing_type_suffix_closing_strategy_single 45083 379994
# closed_True_closing_type_suffix_closing_strategy_shortest_first 45095 370063
# closed_False_closing_type_suffix_closing_strategy_shortest_first 45239 376322
# closed_False_closing_type_suffix_closing_strategy_single_longest 45268 2054046
# closed_False_closing_type_prefix_closing_strategy_single_longest 45305 2059994
# closed_False_closing_type_prefix_closing_strategy_longest_first 45444 397385
# closed_True_closing_type_suffix_closing_strategy_longest_first 45881 391552