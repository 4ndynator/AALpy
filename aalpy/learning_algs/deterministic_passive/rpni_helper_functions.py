from copy import deepcopy

from aalpy.SULs import DfaSUL
from aalpy.automata import DfaState, Dfa, MooreMachine, MooreState, MealyMachine, MealyState


class RpniNode:

    def __init__(self, output):
        self.output = output
        self.children = dict()
        self.prefix = ()

    def copy(self):
        return deepcopy(self)

    def __lt__(self, other):
        return len(self.prefix) < len(other.prefix)

    def __le__(self, other):
        return len(self.prefix) <= len(other.prefix)

    def __eq__(self, other):
        return self.prefix == other.prefix


def check_sequance_mealy(root_node, seq):
    curr_node = root_node
    for i, o in seq:
        i = (i, o)
        if i not in curr_node.children.keys():
            return False
        # if curr_node.children[i].output != o:
        #     return False
        curr_node = curr_node.children[i]
    return True


def check_sequance_dfa_and_moore(root_node, seq):
    curr_node = root_node
    for i, o in seq:
        if i not in curr_node.children.keys():
            return False
        curr_node = curr_node.children[i]
        if curr_node.output != o:
            return False
    return True


def createPTA(data, automaton_type):
    root_node = RpniNode(None)
    for seq in data:
        curr_node = root_node
        for i, o in seq:
            if automaton_type == 'mealy':
                i = (i, o)
            if i not in curr_node.children.keys():
                node = RpniNode(o)
                node.prefix = curr_node.prefix + (i,)
                curr_node.children[i] = node
            curr_node = curr_node.children[i]
    return root_node


def to_automaton(red, automaton_type):
    if automaton_type == 'dfa':
        state, automaton = DfaState, Dfa
    elif automaton_type == 'moore':
        state, automaton = MooreState, MooreMachine
    else:
        state, automaton = MealyState, MealyMachine

    initial_state = None
    prefix_state_map = {}
    for i, r in enumerate(red):
        if automaton_type != 'mealy':
            prefix_state_map[r.prefix] = state(f's{i}', r.output)
        else:
            prefix_state_map[r.prefix] = state(f's{i}')
        if i == 0:
            initial_state = prefix_state_map[r.prefix]

    for r in red:
        for i, c in r.children.items():
            if automaton_type != 'mealy':
                prefix_state_map[r.prefix].transitions[i] = prefix_state_map[c.prefix]
            else:
                prefix_state_map[r.prefix].transitions[i[0]] = prefix_state_map[c.prefix]
                prefix_state_map[r.prefix].output_fun[i[0]] = i[1]

    return automaton(initial_state, list(prefix_state_map.values()))


def visualize_pta(rootNode):
    from pydot import Dot, Node, Edge
    graph = Dot('fpta', graph_type='digraph')

    graph.add_node(Node(str(rootNode.prefix), label=f'{rootNode.output}'))

    queue = [rootNode]
    visited = set()
    visited.add(rootNode.prefix)
    while queue:
        curr = queue.pop(0)
        for i, c in curr.children.items():
            if c.prefix not in visited:
                graph.add_node(Node(str(c.prefix), label=f'{c.output}'))
            graph.add_edge(Edge(str(curr.prefix), str(c.prefix), label=f'{i}'))
            if c.prefix not in visited:
                queue.append(c)
            visited.add(c.prefix)

    graph.add_node(Node('__start0', shape='none', label=''))
    graph.add_edge(Edge('__start0', str(rootNode.prefix), label=''))

    graph.write(path=f'pta.pdf', format='pdf')


def test_rpni_alongside_lstar():
    import random
    from aalpy.learning_algs.deterministic_passive.rpni import RPNI
    from aalpy.learning_algs import run_Lstar
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.utils import generate_random_dfa

    random_dfa = generate_random_dfa(num_states=10, alphabet=[1, 2], num_accepting_states=2)
    alph = random_dfa.get_input_alphabet()
    sul = DfaSUL(random_dfa)
    eq_oracle = RandomWalkEqOracle(alph, sul)
    minimal_model = run_Lstar(alph, sul, eq_oracle, automaton_type='dfa', print_level=1)

    dfa_sul = DfaSUL(minimal_model)
    input_al = minimal_model.get_input_alphabet()
    data = []
    for _ in range(10000):
        dfa_sul.pre()
        seq = []
        for _ in range(5, 20):
            i = random.choice(input_al)
            o = dfa_sul.step(i)
            seq.append((i, o))
        dfa_sul.post()
        data.append(seq)

    rpni_model = RPNI(data, automaton_type='dfa').run_rpni()

    eq_oracle_2 = RandomWalkEqOracle(alph, dfa_sul, num_steps=10000)
    cex = eq_oracle_2.find_cex(rpni_model)
    if cex is None:
        print(rpni_model.size, minimal_model.size)
        print("RPNI SUCESS")
    else:
        assert False
