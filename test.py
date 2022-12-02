from aalpy.SULs.AutomataSUL import AllWeatherSUL
from aalpy.learning_algs.non_deterministic.NonDetKv import run_non_det_KV
from aalpy.utils import generate_random_deterministic_automata
from aalpy.SULs import MealySUL
from aalpy.oracles import RandomWMethodEqOracle
from aalpy.learning_algs import run_KV
from aalpy.utils import get_benchmark_ONFSM

benchmark_onfsm = get_benchmark_ONFSM()
sul = AllWeatherSUL(benchmark_onfsm)

input_alphabet = benchmark_onfsm.get_input_alphabet()

# select any of the oracles
# TODO should receive normal SUL, not all weather one
eq_oracle = RandomWMethodEqOracle(input_alphabet, sul, walks_per_state=10, walk_len=20)

learned_model = run_non_det_KV(input_alphabet, sul, eq_oracle)
