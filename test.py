from aalpy.SULs import StochasticMealySUL
from aalpy.automata.StochasticMealyMachine import smm_to_mdp_conversion
from aalpy.learning_algs import run_non_det_Lstar, run_experimental_stochastic_smm, run_stochastic_Lstar
from aalpy.oracles import RandomWordEqOracle
from aalpy.utils import load_automaton_from_file, model_check_experiment, get_properties_file, get_correct_prop_values
from aalpy.utils.BenchmarkSULs import get_faulty_mqtt_SMM, get_faulty_coffee_machine_MDP, get_small_gridworld, \
    get_minimal_faulty_coffee_machine_SMM, get_weird_coffee_machine_MDP, get_small_pomdp
import aalpy

from random import seed

aalpy.paths.path_to_prism = "C:/Program Files/prism-4.6/bin/prism.bat"
aalpy.paths.path_to_properties = "Benchmarking/prism_eval_props/"


def model_check(experiment):
    smm = load_automaton_from_file(f'./DotModels/MDPs/{experiment}.dot', automaton_type='mdp')
    alph = smm.get_input_alphabet()
    sul = StochasticMealySUL(smm)

    eq_oracle = RandomWordEqOracle(alph, sul, num_walks=500, min_walk_len=5, max_walk_len=20)
    model = run_experimental_stochastic_smm(alph, sul, eq_oracle, n_sampling=1)

    mdp = smm_to_mdp_conversion(model)

    vals, diff = model_check_experiment(get_properties_file(experiment), get_correct_prop_values(experiment), mdp)

    print(f'Property values: {get_correct_prop_values(experiment)}')
    print(f'Computed values: {vals}')
    print('Error for each prop:', [round(d * 100, 2) for d in diff.values()])


model_check('first_grid')
exit()

smm = get_small_gridworld()
alph = smm.get_input_alphabet()
sul = StochasticMealySUL(smm)

eq_oracle = RandomWordEqOracle(alph, sul, num_walks=1000, min_walk_len=3, max_walk_len=20)

model = run_experimental_stochastic_smm(alph, sul, eq_oracle, n_sampling=10)
model.visualize()
