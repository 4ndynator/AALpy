from aalpy.base import SUL
from aalpy.automata import Dfa, MealyMachine, MooreMachine, Onfsm, Mdp, StochasticMealyMachine, MarkovChain


class DfaSUL(SUL):
    """
    System under learning for DFAs.
    """

    def __init__(self, dfa: Dfa):
        super().__init__()
        self.dfa = dfa

    def pre(self):
        """
        Resets the dfa to the initial state.
        """
        self.dfa.reset_to_initial()

    def post(self):
        pass

    def step(self, letter):
        """
        If the letter is empty/None check is preform to see if the empty string is accepted by the DFA.

        Args:

            letter: single input or None representing the empty string

        Returns:

            output of the dfa.step method (whether the next state is accepted or not)

        """
        return self.dfa.step(letter)


class MdpSUL(SUL):
    def __init__(self, mdp: Mdp):
        super().__init__()
        self.mdp = mdp

    def query(self, word: tuple) -> list:
        initial_output = self.pre()
        out = [initial_output]
        for letter in word:
            out.append(self.step(letter))
        self.post()
        return out

    def pre(self):
        self.mdp.reset_to_initial()
        return self.mdp.current_state.output

    def post(self):
        pass

    def step(self, letter):
        return self.mdp.step(letter)


class McSUL(SUL):
    def __init__(self, mdp: MarkovChain):
        super().__init__()
        self.mc = mdp

    def query(self, word: tuple) -> list:
        initial_output = self.pre()
        out = [initial_output]
        for letter in word:
            out.append(self.step(letter))
        self.post()
        return out

    def pre(self):
        self.mc.reset_to_initial()
        return self.mc.current_state.output

    def post(self):
        pass

    def step(self, letter=None):
        return self.mc.step()


class MealySUL(SUL):
    """
    System under learning for Mealy machines.
    """

    def __init__(self, mm: MealyMachine):
        super().__init__()
        self.mm = mm

    def pre(self):
        """ """
        self.mm.reset_to_initial()

    def post(self):
        """ """
        pass

    def step(self, letter):
        """
        Args:

            letter: single non-Null input

        Returns:

            output of the mealy.step method (output based on the input and the current state)

        """
        return self.mm.step(letter)


class MooreSUL(SUL):
    """
    System under learning for Mealy machines.
    """

    def __init__(self, moore_machine: MooreMachine):
        super().__init__()
        self.mm = moore_machine

    def pre(self):
        """ """
        self.mm.reset_to_initial()

    def post(self):
        """ """
        pass

    def step(self, letter):
        return self.mm.step(letter)


class OnfsmSUL(SUL):
    def __init__(self, mdp: Onfsm):
        super().__init__()
        self.onfsm = mdp

    def pre(self):
        self.onfsm.reset_to_initial()

    def post(self):
        pass

    def step(self, letter):
        return self.onfsm.step(letter)


class StochasticMealySUL(SUL):
    def __init__(self, smm: StochasticMealyMachine):
        super().__init__()
        self.smm = smm

    def pre(self):
        self.smm.reset_to_initial()

    def post(self):
        pass

    def step(self, letter):
        return self.smm.step(letter)


class AllWeatherSUL(SUL):
    def __init__(self, onfsm: Onfsm):
        super().__init__()
        self.onfsm = onfsm
        self.current_states_prefixes = []

    def pre(self):
        self.onfsm.reset_to_initial()
        self.current_states_prefixes = [((), ())]

    def post(self):
        pass

    def query(self, word: tuple) -> set:
        self.pre()
        # Empty string for DFA
        out = [self.step(letter) for letter in word][-1]
        self.post()
        self.num_queries += 1
        self.num_steps += len(word)
        return out

    def step(self, letter):
        new_reached_states = []
        for inputs, outputs in self.current_states_prefixes:
            self.onfsm.reset_to_initial()
            new_inputs, new_outputs = inputs, outputs
            if inputs and outputs:
                for i, o in zip(inputs, outputs):
                    self.onfsm.step_to(i, o)
            for output, new_state in self.onfsm.current_state.transitions[letter]:
                new_inputs += (letter,)
                new_outputs += (output,)
                new_reached_states.append((new_inputs, new_outputs))

        self.current_states_prefixes = new_reached_states
        return set([o[-1] for _, o in new_reached_states])

