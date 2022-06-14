from itertools import product

from aalpy.SULs import MdpSUL
from aalpy.learning_algs import run_stochastic_Lstar
from aalpy.oracles import RandomWordEqOracle
from aalpy.utils import generate_random_mdp, generate_random_smm

automata_size = [5, 10, 15, 20, 30, 50, ]
inputs_size = [2, 3, 5, 7, 9]
outputs_size = [2, 5, 10, 15, 20]
inputs_size = [7]
outputs_size = [15]


def learn(mdp, type):
    input_al = mdp.get_input_alphabet()
    sul = MdpSUL(mdp)
    eq_oracle = RandomWordEqOracle(input_al, sul, num_walks=1000, min_walk_len=4, max_walk_len=20)
    return run_stochastic_Lstar(input_al, sul, eq_oracle, automaton_type=type, cex_processing=None, print_level=0,
                                return_data=True)


num_queries_mdp = []
num_queries_smm = []

# i = 0
# for p in product(automata_size, inputs_size, outputs_size):
#     num_states, num_inputs, num_outputs = p
#     if num_inputs > num_outputs:
#         continue
#
#     print(i)
#     i += 1
#
#     # random_mdp = generate_random_mdp(num_states=num_states, input_size=num_inputs, output_size=num_outputs)
#     random_smm = generate_random_smm(num_states=num_states, input_size=num_inputs, output_size=num_outputs)
#     random_smm = random_smm.to_mdp()
#
#     _, mdp_data = learn(random_smm, 'mdp')
#     _, smm_data = learn(random_smm, 'smm')
#
#     num_queries_mdp.append(mdp_data['queries_learning'] + mdp_data['queries_eq_oracle'])
#     num_queries_smm.append(smm_data['queries_learning'] + smm_data['queries_eq_oracle'])
#
# print(num_queries_mdp)
# print(num_queries_smm)

num_queries_mdp_3_7 = [77115, 85440, 36326, 132485, 250055, 343526]
num_queries_smm_3_7 = [23511, 14287, 17106, 55482, 50935, 99730]

num_queries_mdp_4_10 = [54654, 265240, 245245, 238944, 320026, 1170086]
num_queries_smm_4_10 = [7122, 42637, 32431, 51821, 75703, 204150]

num_queries_mdp_7_15 = [237731, 397386, 924637, 2066456, 4117725, 4774201]
num_queries_smm_7_15 = [15733, 19148, 52214, 106436, 157414, 605491]

# pairs = [(num_queries_mdp_3_7, num_queries_smm_3_7), (num_queries_mdp_4_10, num_queries_smm_4_10),
#          (num_queries_mdp_7_15, num_queries_smm_7_15)]
#
# for mdp, smm in pairs:
#     save = []
#     for m, s in zip(mdp, smm):
#         save.append(100 - round(s / m * 100, 2))
#     print(save)

smm_save_3_7 = [69.51, 83.28, 52.91, 58.12, 79.63, 70.97]
smm_save_4_10 = [86.97, 83.93, 86.78, 78.31, 76.34, 82.55]
smm_save_7_15 = [93.38, 95.18, 94.35, 94.85, 96.18, 87.32]


def plot_queries_smm_as_base():
    import matplotlib.pyplot as plt

    plt.plot(automata_size, smm_save_3_7, label='I:3,O: 7)')
    plt.plot(automata_size, smm_save_4_10, label='I:4,O: 10')
    plt.plot(automata_size, smm_save_7_15, label='I:7,O: 15')

    plt.xticks(automata_size)

    plt.grid()
    plt.legend()
    plt.show()


plot_queries_smm_as_base()
