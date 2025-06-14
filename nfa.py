"""
nfa.py: Non-deterministic Finite Automaton implementation.
"""
from dfa import DFA # Import DFA class

class NFA(DFA): # Inherit from DFA
    def __init__(self, nfa=None, filename=None):
        """
        Initialize NFA from given dict or input file.
        nfa: dict with keys 'Q', 'Σ', 'δ', 'q0', 'F'
        """
        if nfa is not None:
            self.nfa = nfa
        else:
            self.nfa = self.load_nfa(filename)
        self.states = set(self.nfa['Q'])
        self.alphabet = set(self.nfa['Σ'])
        # ensure epsilon symbol is present in the alphabet
        if 'ε' not in self.alphabet:
            self.alphabet.add('ε')
        # transitions: mapping (state, symbol) -> set(states)
        self.transitions = {k: set(v) for k, v in self.nfa['δ'].items()}
        self.start_state = self.nfa['q0']
        self.accept_states = set(self.nfa['F'])

        # Convert NFA to DFA and initialize DFA part
        dfa_definition = self.to_dfa()
        super().__init__(dfa=dfa_definition) # Initialize DFA parent class

    def load_nfa(self, filename):
        """
        Load NFA definition from file similar to DFA format: Q, Σ, δ, q0, F sections ending with '#'.

        Args:
            filename (str): The name of the file containing the NFA definition. If None, prompt user interactively.

        Returns:
            dict: A dictionary representing the NFA with keys 'Q', 'Σ', 'δ', 'q0', 'F'.

        Raises:
            ValueError: If the NFA input file format is incorrect or incomplete.
        """
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('//')]
            # find section delimiters
            section_idxs = [i for i, ln in enumerate(lines) if ln.endswith('#')]
            if len(section_idxs) < 5:
                raise ValueError('NFA input file format is incorrect or incomplete.')
            # parse Q and Σ
            Q = [s.strip() for s in lines[0].replace('#','').split(',') if s.strip()]
            sigma = [s.strip() for s in lines[1].replace('#','').split(',') if s.strip()]
            # parse transitions from line 2 to section_idxs[2]
            delta = {}
            for i in range(2, section_idxs[2]+1):
                entry = lines[i].replace('#','')
                if not entry:
                    continue
                lhs, rhs = entry.split('=')
                st, sym = [x.strip() for x in lhs.split(',')]
                dst = rhs.strip()
                key = (st, sym)
                delta.setdefault(key, set()).add(dst)
            # parse start and accepting
            q0 = lines[section_idxs[3]].replace('#','').strip()
            F = [s.strip() for s in lines[section_idxs[4]].replace('#','').split(',') if s.strip()]
            return {'Q': Q, 'Σ': sigma, 'δ': delta, 'q0': q0, 'F': F}
        # interactive input if no file provided
        print("Description of NFA format: (Q, Σ, δ, q0, F)")
        Q = input("Enter the set of states (Q) (comma-separated): ").split(',')
        Q = [s.strip() for s in Q if s.strip()]

        Sigma = input("Enter the input alphabet (Σ) (comma-separated, use ε for epsilon): ").split(',')
        sigma = [s.strip() for s in Sigma if s.strip()]

        print("Enter the transition function δ:")
        print("Format: current_state,input_symbol=new_state (Enter 'done' to stop)")
        delta = {}
        while True:
            entry = input("δ: ")
            if entry.lower() == 'done':
                break
            try:
                lhs, rhs = entry.split('=')
                st, sym = [x.strip() for x in lhs.split(',')]
                if st not in Q or sym not in sigma:
                    print(f"Invalid state or symbol {st}, {sym}. Try again.")
                    continue
                dst = rhs.strip()
                if dst not in Q:
                    print(f"Invalid destination state {dst}. Try again.")
                    continue
                key = (st, sym)
                delta.setdefault(key, set()).add(dst)
            except:
                print("Invalid format. Try again.")

        def take_q0():
            q0 = input("Enter the start state: ").strip()
            if q0 not in Q:
                print(f"Start state {q0} is not valid. Please try again.")
                return take_q0()
            return q0

        q0 = take_q0()
        F = input("Enter the set of accepting states (comma-separated): ").split(',')
        F = [s.strip() for s in F if s.strip() in Q]
        return {'Q': Q, 'Σ': sigma, 'δ': delta, 'q0': q0, 'F': F}

    def epsilon_closure(self, states):
        """
        Compute the epsilon closure of the given set of states.
        Epsilon closure of a state is the set of states reachable from it
        using only epsilon transitions (including the state itself).
        """
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            # Follow epsilon transitions
            for next_state in self.transitions.get((state, 'ε'), []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure

    def move(self, states, symbol):
        """
        Move to the next states given the current states and an input symbol.
        This function considers only the transitions for the given symbol.
        """
        next_states = set()
        for state in states:
            next_states.update(self.transitions.get((state, symbol), []))
        return next_states

    def accepts(self, input_string):
        """
        Check if the NFA accepts the given input string.
        The NFA accepts the string if there exists a sequence of transitions
        for the string that leads to an accepting state.
        """
        current_states = self.epsilon_closure({self.start_state})
        
        for symbol in input_string:
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol {symbol} not in alphabet {self.alphabet}")
            current_states = self.epsilon_closure(self.move(current_states, symbol))
            if not current_states: # No valid transitions, dead end
                return False

        # accept if any current state is accepting
        return bool(current_states & self.accept_states)

    def to_dfa(self):
        """
        Converts the NFA to an equivalent DFA using subset construction.
        Returns a dictionary defining the DFA, compatible with the DFA class.
        """
        dfa_alphabet = self.alphabet - {'ε'}
        
        # DFA states are frozensets of NFA states
        nfa_q0_epsilon_closure = self.epsilon_closure({self.start_state})
        dfa_q0_fset = frozenset(nfa_q0_epsilon_closure)

        worklist = [dfa_q0_fset]
        # dfa_states_fset stores all discovered DFA states (as frozensets of NFA states)
        dfa_states_fset = {dfa_q0_fset}
        # dfa_transitions_fset stores DFA transitions: (source_fset, symbol) -> target_fset
        dfa_transitions_fset = {}

        head = 0
        while head < len(worklist):
            current_dfa_fset = worklist[head]
            head += 1

            for symbol in dfa_alphabet:
                next_nfa_states_on_symbol = set()
                for nfa_state in current_dfa_fset:
                    next_nfa_states_on_symbol.update(self.transitions.get((nfa_state, symbol), set()))
                
                target_dfa_fset = frozenset(self.epsilon_closure(next_nfa_states_on_symbol))
                
                dfa_transitions_fset[(current_dfa_fset, symbol)] = target_dfa_fset
                
                if target_dfa_fset not in dfa_states_fset:
                    dfa_states_fset.add(target_dfa_fset)
                    worklist.append(target_dfa_fset)

        # Convert frozenset states to string names for the DFA definition
        fset_to_str_map = {}
        dfa_q_str_list = []
        
        # Ensure consistent naming for the dead state if it exists
        dead_state_frozenset = frozenset()
        if dead_state_frozenset in dfa_states_fset:
            fset_to_str_map[dead_state_frozenset] = "{DEAD}"

        for fs_state in dfa_states_fset:
            if fs_state not in fset_to_str_map: # Avoid re-processing dead state if already named
                if not fs_state: # Should be caught by the above, but as a safeguard
                     name = "{DEAD}"
                else:
                    name = "{" + ",".join(sorted(list(str(s) for s in fs_state))) + "}"
                fset_to_str_map[fs_state] = name
            dfa_q_str_list.append(fset_to_str_map[fs_state])

        dfa_q0_str = fset_to_str_map[dfa_q0_fset]
        
        dfa_f_str_list = []
        for fs_state in dfa_states_fset:
            if any(nfa_s in self.accept_states for nfa_s in fs_state):
                dfa_f_str_list.append(fset_to_str_map[fs_state])

        dfa_delta_dict = {}
        for (source_fset, symbol), target_fset in dfa_transitions_fset.items():
            source_name = fset_to_str_map[source_fset]
            target_name = fset_to_str_map[target_fset]
            dfa_delta_dict[(source_name, symbol)] = target_name
            
        # Ensure the dead state (if it exists) has transitions to itself for all symbols
        dead_state_name = "{DEAD}"
        if dead_state_name in dfa_q_str_list:
            for symbol in dfa_alphabet:
                if (dead_state_name, symbol) not in dfa_delta_dict: # If not already defined (e.g. if dead state was only a target)
                    dfa_delta_dict[(dead_state_name, symbol)] = dead_state_name
        
        # Ensure all states have transitions for all symbols (explicitly to dead state if needed)
        # This makes the DFA complete.
        if dead_state_name in dfa_q_str_list or not dfa_alphabet: # if dead state exists or no symbols to transition on
             pass # Handled by dead_state_name transitions or if no alphabet, no transitions needed beyond initial setup
        elif dfa_alphabet : # If there's an alphabet but no dead state created yet, and some transitions are missing
            # Check if a dead state needs to be implicitly created
            needs_dead_state_creation = False
            for state_name in dfa_q_str_list:
                for symbol in dfa_alphabet:
                    if (state_name, symbol) not in dfa_delta_dict:
                        needs_dead_state_creation = True
                        break
                if needs_dead_state_creation:
                    break
            
            if needs_dead_state_creation:
                if dead_state_name not in dfa_q_str_list: # Add dead state if not present
                    dfa_q_str_list.append(dead_state_name)
                for state_name in dfa_q_str_list: # Iterate again, now including potential new dead_state_name
                     for symbol in dfa_alphabet:
                        if (state_name, symbol) not in dfa_delta_dict:
                            dfa_delta_dict[(state_name, symbol)] = dead_state_name


        dfa_definition = {
            'Q': dfa_q_str_list,
            'Σ': sorted(list(dfa_alphabet)), # DFA class might expect list, sort for consistency
            'δ': dfa_delta_dict,
            'q0': dfa_q0_str,
            'F': dfa_f_str_list
        }
        
        return dfa_definition

    def visualize_dfa_equivalent(self, in_string, index_dir='nfa_to_dfa_video_frames', delay=1.0, embed_in_index=True):
        """
        Visualizes the DFA equivalent of this NFA processing an input string.
        Uses the visualization_video method from the parent DFA class.
        """
        print(f"Visualizing DFA equivalent for input string: {in_string}")
        # The visualization_video method is inherited from DFA
        # and will use the DFA definition created in __init__
        return self.visualization_video(in_string, index_dir=index_dir, delay=delay, embed_in_index=embed_in_index)

    def print_nfa(self):
        """
        Print the NFA in a readable format.
        """
        print("NFA:")
        print(f"States (Q): {', '.join(self.states)}")
        print(f"Alphabet (Σ): {', '.join(self.alphabet)}")
        print("Transitions (δ):")
        for (state, symbol), next_states in self.transitions.items():
            print(f"  {state}, {symbol} -> {', '.join(next_states)}")
        print(f"Start state (q0): {self.start_state}")
        print(f"Accept states (F): {', '.join(self.accept_states)}")
    
    
        



__main__ = '__main__'
if __name__ == '__main__':
    nfa = NFA(filename="nfa_input.txt")
    nfa.print_nfa()
    # Example of visualizing the DFA equivalent
    visualization_result = nfa.visualize_dfa_equivalent("101", index_dir='nfa_to_dfa_video_frames')
    if visualization_result:
        print(f"Visualization HTML (DFA equivalent) generated at: {visualization_result['html_path']}")
        print(f"Input string accepted (DFA equivalent): {visualization_result['accepted']}")
