import random
from collections import defaultdict
from typing import Dict, Generic, List, Tuple

from aalpy.base import Automaton, AutomatonState
# TODO edit setup to include this in base?
from aalpy.base.Automaton import OutputType, InputType


class MdpState(AutomatonState, Generic[InputType, OutputType]):
    def __init__(self, state_id, output=None):
        super().__init__(state_id)
        self.output : OutputType = output
        # each child is a tuple (Node(output), probability)
        self.transitions : Dict[InputType, List[Tuple[MdpState, float]]] = defaultdict(list)


class Mdp(Automaton[MdpState[InputType, OutputType]]):
    """Markov Decision Process."""

    def __init__(self, initial_state: MdpState, states: list):
        super().__init__(initial_state, states)

    def reset_to_initial(self):
        self.current_state = self.initial_state

    def step(self, letter):
        """Next step is determined based on transition probabilities of the current state.

        Args:

            letter: input

        Returns:

            output of the current state
        """
        if letter is None:
            return self.current_state.output

        probability_distributions = [i[1] for i in self.current_state.transitions[letter]]
        states = [i[0] for i in self.current_state.transitions[letter]]

        new_state = random.choices(states, probability_distributions, k=1)[0]

        self.current_state = new_state
        return self.current_state.output

    def step_to(self, inp, out):
        """Performs a step on the automaton based on the input `inp` and output `out`.

        Args:

            inp: input
            out: output

        Returns:

            output of the reached state, None otherwise
        """
        for new_state in self.current_state.transitions[inp]:
            if new_state[0].output == out:
                self.current_state = new_state[0]
                return out
        return None

    def to_state_setup(self):
        state_setup_dict = {}

        # ensure initial state is first in the list
        if self.states[0] != self.initial_state:
            self.states.remove(self.initial_state)
            self.states.insert(0, self.initial_state)

        for s in self.states:
            state_setup_dict[s.state_id] = (s.output, {k: [(node.state_id, prob) for node, prob in v]
                                                       for k, v in s.transitions.items()})

        return state_setup_dict

    def copy(self):
        from aalpy.utils import mdp_from_state_setup
        return mdp_from_state_setup(self.to_state_setup())