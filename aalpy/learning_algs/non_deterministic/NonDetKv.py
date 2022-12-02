import time

from aalpy.automata import Dfa, DfaState, MealyState, MealyMachine, MooreState, MooreMachine, OnfsmState, Onfsm
from aalpy.base import Oracle, SUL
from aalpy.utils.HelperFunctions import print_learning_info
from .NonDetClassificationTree import NonDetClassificationTree
from ...base.SUL import CacheSUL

print_options = [0, 1, 2, 3]


def run_non_det_KV(alphabet: list, sul: SUL, eq_oracle: Oracle,
                   max_learning_rounds=None, return_data=False, print_level=2):
    """
    Executes the KV algorithm.

    Args:

        alphabet: input alphabet

        sul: system under learning

        eq_oracle: equivalence oracle

        automaton_type: type of automaton to be learned. One of 'dfa', 'mealy', 'moore'

        max_learning_rounds: number of learning rounds after which learning will terminate (Default value = None)

        return_data: if True, a map containing all information(runtime/#queries/#steps) will be returned
            (Default value = False)

        print_level: 0 - None, 1 - just results, 2 - current round and hypothesis size, 3 - educational/debug
            (Default value = 2)


    Returns:

        automaton of type automaton_type (dict containing all information about learning if 'return_data' is True)

    """

    assert print_level in print_options

    start_time = time.time()
    eq_query_time = 0
    learning_rounds = 0

    initial_state = OnfsmState(state_id='s0')

    for a in alphabet:
        output = sul.query((a,))[-1]
        initial_state.transitions[a].append((output, initial_state))

    hypothesis = Onfsm(initial_state, [initial_state])

    # Perform an equivalence query on this automaton
    eq_query_start = time.time()
    cex = eq_oracle.find_cex(hypothesis)
    eq_query_time += time.time() - eq_query_start
    already_found = False

    while True:
        if len(cex[0]) > 1:
            break

        single_input, single_output = cex[0][0], cex[1][0]
        initial_state.transitions[single_input].append((single_output, initial_state))

        eq_query_start = time.time()
        cex = eq_oracle.find_cex(hypothesis)
        eq_query_time += time.time() - eq_query_start

        if cex is None:
            already_found = True

    # initialise the classification tree to have a root
    # labeled with the empty word as the distinguishing string
    # and two leaves labeled with access strings cex and empty word

    cex = tuple(cex[0]), tuple(cex[1])
    classification_tree = NonDetClassificationTree(alphabet=alphabet, sul=sul, cex=cex)

    while True and not already_found:
        learning_rounds += 1
        if max_learning_rounds and learning_rounds - 1 == max_learning_rounds:
            break

        hypothesis = classification_tree.gen_hypothesis()

        if print_level == 2:
            print(f'\rHypothesis {learning_rounds}: {hypothesis.size} states.', end="")

        if print_level == 3:
            # would be nice to have an option to print classification tree
            print(f'Hypothesis {learning_rounds}: {hypothesis.size} states.')

        if counterexample_not_valid(hypothesis, cex):
            # Perform an equivalence query on this automaton
            eq_query_start = time.time()
            cex = eq_oracle.find_cex(hypothesis)
            eq_query_time += time.time() - eq_query_start

            if cex is None:
                break
            else:
                cex = tuple(cex[0]), tuple(cex[1])

            if print_level == 3:
                print('Counterexample', cex)

        classification_tree.update(cex, hypothesis)

    total_time = round(time.time() - start_time, 2)
    eq_query_time = round(eq_query_time, 2)
    learning_time = round(total_time - eq_query_time, 2)

    info = {
        'learning_rounds': learning_rounds,
        'automaton_size': hypothesis.size,
        'queries_learning': sul.num_queries,
        'steps_learning': sul.num_steps,
        'queries_eq_oracle': eq_oracle.num_queries,
        'steps_eq_oracle': eq_oracle.num_steps,
        'learning_time': learning_time,
        'eq_oracle_time': eq_query_time,
        'total_time': total_time,
        'classification_tree': classification_tree,
        'cache_saved': sul.num_cached_queries,
    }

    if print_level > 0:
        if print_level == 2:
            print("")
        print_learning_info(info)

    if return_data:
        return hypothesis, info

    return hypothesis


def counterexample_not_valid(hypothesis, cex):
    if cex is None:
        return True
    hypothesis.reset_to_initial()
    for i, o in zip(cex[0], cex[1]):
        out = hypothesis.step_to(i, o)
        if out is None:
            return False
    return True
