from collections import Counter
from random import choice, random

from aalpy.automata import Onfsm, OnfsmState
from aalpy.base import Automaton
from aalpy.learning_algs.non_deterministic.TraceTree import SULWrapper
from aalpy.learning_algs.stochastic_no_stat.TraceTree import Node


class ExperimentalStochasticObservationTable:

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

        pta_root = Node(None)
        for s in update_S:
            for e in update_E:
                num_s_e_sampled = 0
                # self.add_to_pta(pta_root, s, e)
                # if self.sampling_counter[s[0] + e] >= len(s[0] + e) + 1 * 2:
                #     continue
                if self.sampling_counter[s + e] < 100:
                    while num_s_e_sampled < self.n_samples:
                        output = tuple(self.sul.query(s[0] + e))
                        if output[:len(s[1])] == s[1]:
                            num_s_e_sampled += 1
                            self.sampling_counter[s + e] += 1

        # resample_size = len(self.S) + len(self.S) * len(self.A) * len(self.E) * 4
        # for _ in range(resample_size):
        #     self.tree_query(pta_root)

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

    def is_row_closed(self, r, s_set):
        for s in s_set:
            if self.are_rows_compatible(r, s):
                return True
        return False

    def get_compatible_row(self, r):
        for s in self.S:
            s_h = self.row_to_hashable(s)
            if self.are_rows_compatible(r, s):
                return s_h
        return None

    def are_rows_compatible(self, r1, r2):
        for cell1, cell2 in zip(r1, r2):
            if len(cell1) >= len(cell2):
                if not cell1.issuperset(cell2):
                    return False
            else:
                if not cell2.issuperset(cell1):
                    return False
        return True

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

    def add_transition_probabilities(self, hypothesis):
        from aalpy.automata import StochasticMealyState, StochasticMealyMachine
        initial_state = None
        stochastic_states = []
        prefix_map = {}

        for state in hypothesis.states:
            smm_state = StochasticMealyState(state.state_id)
            prefix = []
            for i, o in zip(state.prefix[0], state.prefix[1]):
                prefix.extend([i, o])
            smm_state.prefix = prefix
            print(len(prefix))
            prefix_map[state.prefix] = smm_state

            if not state.prefix[0]:
                initial_state = smm_state
            stochastic_states.append(smm_state)

        assert initial_state
        for state in hypothesis.states:
            tree_node = self.sul.pta.get_to_node(state.prefix[0], state.prefix[1])
            smm_state = prefix_map[state.prefix]
            for a in self.A:
                of = tree_node.get_output_frequencies(a[0])
                for output, reached_state in state.transitions[a[0]]:
                    reached_state_smm = prefix_map[reached_state.prefix]
                    probability = of[output] / sum(of.values())
                    smm_state.transitions[a[0]].append((reached_state_smm, output, probability))

        smm = StochasticMealyMachine(initial_state, stochastic_states)
        return smm
