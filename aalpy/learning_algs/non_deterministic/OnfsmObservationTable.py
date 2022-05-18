from collections import Counter
from random import choice, random
from statistics import mean

from aalpy.automata import Onfsm, OnfsmState
from aalpy.base import Automaton
from aalpy.learning_algs.non_deterministic.TraceTree import SULWrapper
from aalpy.learning_algs.stochastic.StochasticTeacher import Node

class NonDetObservationTable:

    def __init__(self, alphabet: list, sul: SULWrapper, n_sampling):
        """
        Construction of the non-deterministic observation table.

        Args:

            alphabet: input alphabet
            sul: system under learning
            n_sampling: number of samples to be performed for each cell
        """
        assert alphabet is not None and sul is not None

        self.A = [tuple([a]) for a in alphabet]
        self.S = list()  # prefixes of S

        self.E = [tuple([a]) for a in alphabet]

        self.n_samples = n_sampling
        self.closing_counter = 0

        self.sul = sul

        self.sampling_counter = Counter()

        empty_word = tuple()

        # Elements of S are in form that is presented in 'Learning Finite State Models of Observable Nondeterministic
        # Systems in a Testing Context'. Each element of S is a (inputs, outputs) tuple, where first element of the
        # tuple are inputs and second element of the tuple are outputs associated with inputs.
        self.S.append((empty_word, empty_word))

    def get_row_to_close(self):
        """
        Get row for that need to be closed.

        Returns:

            row that will be moved to S set and closed
        """
        s_rows = set()
        update_S_dot_A = self.get_extended_S()

        for s in self.S.copy():
            s_rows.add(self.row_to_hashable(s))

        for t in update_S_dot_A:
            row_t = self.row_to_hashable(t)
            if row_t not in s_rows:
                self.closing_counter += 1
                self.S.append(t)
                return t

        self.closing_counter = 0
        return None

    def get_extended_S(self):
        """
        Helper generator function that returns extended S, or S.A set.
        For all values in the cell, create a new row where inputs is parent input plus element of alphabet, and
        output is parent output plus value in cell.

        Returns:

            extended S set.
        """

        S_dot_A = []
        for row in self.S:
            curr_node = self.sul.pta.get_to_node(row[0], row[1])
            for a in self.A:
                trace = self.sul.pta.get_all_traces(curr_node, a)

                for t in trace:
                    new_row = (row[0] + a, row[1] + (t[-1],))
                    if new_row not in self.S:
                        S_dot_A.append(new_row)
        return S_dot_A

    def update_obs_table(self, s_set=None, e_set: list = None):
        """
        Perform the membership queries.
        With  the  all-weather  assumption,  each  output  query  is  tried  a  number  of  times  on  the  system,
        and  the  driver  reports  the  set  of  all  possible  outputs.

        Args:

            s_set: Prefixes of S set on which to preform membership queries (Default value = None)
            e_set: Suffixes of E set on which to perform membership queries
        """

        update_S = s_set if s_set else self.S + self.get_extended_S()
        update_E = e_set if e_set else self.E

        # update_S, update_E = self.S + self.S_dot_A, self.E

        num_samples = 0
        root_node = Node('dummy')
        for s in update_S:
            for e in update_E:
                num_s_e_sampled = 0
                # if self.sampling_counter[s[0] + e] >= len(s[0] + e) + 1 * 2:
                #     continue
                if self.sampling_counter[s[0] + e] < mean(self.sampling_counter.values()) - 10:
                    uncertainty = mean(self.sampling_counter.values()) - self.sampling_counter[s[0] + e]
                    num_samples += uncertainty
                    self.add_to_pta(root_node, s, e, num_samples)

        for _ in range(num_samples * 2):
            self.tree_query(root_node)

    def clean_obs_table(self):
        """
        Moves duplicates from S to S_dot_A. The entries in S_dot_A which are based on the moved row get deleted.
        The table will be smaller and more efficient.

        """
        # just for testing without cleaning
        # return False

        tmp_S = self.S.copy()
        tmp_both_S = self.S + self.get_extended_S()
        hashed_rows_from_s = set()

        tmp_S.sort(key=lambda t: len(t[0]))

        for s in tmp_S:
            hashed_s_row = self.row_to_hashable(s)
            if hashed_s_row in hashed_rows_from_s:
                if s in self.S:
                    self.S.remove(s)
                size = len(s[0])
                for row_prefix in tmp_both_S:
                    s_both_row = (row_prefix[0][:size], row_prefix[1][:size])
                    if s != row_prefix and s == s_both_row:
                        if row_prefix in self.S:
                            self.S.remove(row_prefix)
            else:
                hashed_rows_from_s.add(hashed_s_row)

    def gen_hypothesis(self) -> Automaton:
        """
        Generate automaton based on the values found in the observation table.

        Returns:

            Current hypothesis

        """
        state_distinguish = dict()
        states_dict = dict()
        initial = None

        stateCounter = 0
        for prefix in self.S:
            state_id = f's{stateCounter}'
            states_dict[prefix] = OnfsmState(state_id)

            states_dict[prefix].prefix = prefix
            state_distinguish[self.row_to_hashable(prefix)] = states_dict[prefix]

            if prefix == self.S[0]:
                initial = states_dict[prefix]
            stateCounter += 1

        for prefix in self.S:
            curr_node = self.sul.pta.get_to_node(prefix[0], prefix[1])
            for a in self.A:
                trace = self.sul.pta.get_all_traces(curr_node, a)
                for t in trace:
                    reached_row = (prefix[0] + a, prefix[1] + (t[-1],))
                    if self.row_to_hashable(reached_row) not in state_distinguish.keys():
                        print('reeee')
                    state_in_S = state_distinguish[self.row_to_hashable(reached_row)]
                    assert state_in_S  # shouldn't be necessary because of the if condition
                    states_dict[prefix].transitions[a[0]].append((t[-1], state_in_S))

        assert initial
        automaton = Onfsm(initial, [s for s in states_dict.values()])
        automaton.characterization_set = self.E

        return automaton

    def row_to_hashable(self, row_prefix):
        """
        Creates the hashable representation of the row. Frozenset is used as the order of element in each cell does not
        matter

        Args:

            row_prefix: prefix of the row in the observation table

        Returns:

            hashable representation of the row

        """
        row_repr = tuple()
        curr_node = self.sul.pta.get_to_node(row_prefix[0], row_prefix[1])

        for e in self.E:
            cell = self.sul.pta.get_all_traces(curr_node, e)
            while not cell:
                self.update_obs_table(s_set=[row_prefix], e_set=[e])
                cell = self.sul.pta.get_all_traces(curr_node, e)

            row_repr += (frozenset(cell),)

        return row_repr

    def add_to_pta(self, root_node, prefix, suffix, uncertainty_value):
        curr_node = root_node

        for i, o in zip(prefix[0], prefix[1]):
            curr_node.input_frequencies[i] += uncertainty_value
            child = curr_node.get_child(i, o)
            if child:
                curr_node = child
            else:
                new_node = Node(o)
                curr_node.children[i][o] = new_node
                curr_node = new_node

        for s in suffix:
            child = curr_node.get_child(s, 'dummy')
            if child:
                curr_node = child
            else:
                new_node = Node('dummy')
                curr_node.children[s]['dummy'] = new_node
                curr_node = new_node

    def tree_query(self, root_node):
        self.sul.pre()
        curr_node = root_node

        inputs = []
        outputs = []

        while True:

            if curr_node.children:
                frequency_sum = sum(curr_node.input_frequencies.values())
                if frequency_sum == 0:
                    # uniform sampling in case we have no information
                    inp = choice(list(curr_node.children.keys()))
                else:
                    # use float random rather than integers to be able to work with non-integer frequency information
                    selection_value = random() * frequency_sum
                    inp = None
                    for i in curr_node.input_frequencies.keys():
                        inp = i
                        selection_value -= curr_node.input_frequencies[i]
                        if selection_value <= 0:
                            break
                    # curr_node.input_frequencies[inp] -= 1

                inputs.append(inp)
                out = self.sul.step(inp)
                new_node = curr_node.get_child(inp, out)

                if new_node:
                    outputs.append(out)
                    curr_node = new_node
                else:
                    self.sampling_counter[inputs] += 1
                    self.sul.post()
                    return
            else:
                curr_node = root_node
                for i, o in zip(inputs, outputs):
                    # self.curr_node.input_frequencies[i] -= 1
                    curr_node = curr_node.get_child(i, o)
                self.sul.post()
                return