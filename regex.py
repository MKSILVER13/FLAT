\
from nfa import NFA
from dfa import DFA
import re # Ensure 're' is imported

class RegExp:
    def __init__(self, pattern):
        self.pattern = pattern
        self._state_counter = 0  # For generating unique NFA state names

    def _generate_state_name(self):
        self._state_counter += 1
        return f"s{self._state_counter}"

    def _add_concat_operator(self, infix_regex):
        """Adds explicit concatenation operator '.' where needed."""
        output_list = []
        for i, token in enumerate(infix_regex):
            output_list.append(token)
            if i < len(infix_regex) - 1:
                current_char = token
                next_char = infix_regex[i+1]
                if (current_char.isalnum() or current_char == 'ε' or current_char == ')' or current_char == '*') and (next_char.isalnum() or next_char == 'ε' or next_char == '('):
                    output_list.append('.')
        return "".join(output_list)

    def _to_postfix(self, infix_regex_with_concat):
        """Converts infix regex (with explicit concatenation) to postfix."""
        precedence = {'|': 1, '.': 2, '*': 3} # Higher value means higher precedence
        postfix = []
        operator_stack = []

        for token in infix_regex_with_concat:
            if token.isalnum() or token == 'ε': # Operand
                postfix.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    postfix.append(operator_stack.pop())
                if not operator_stack or operator_stack[-1] != '(':
                    raise ValueError("Mismatched parentheses in regex")
                operator_stack.pop()  # Pop '('
            else: # Operator
                while (operator_stack and
                       operator_stack[-1] != '(' and
                       precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0)):
                    postfix.append(operator_stack.pop())
                operator_stack.append(token)

        while operator_stack:
            if operator_stack[-1] == '(':
                raise ValueError("Mismatched parentheses in regex")
            postfix.append(operator_stack.pop())
        
        return "".join(postfix)

    def _postfix_to_nfa(self, postfix):
        """
        Converts a postfix regular expression to an NFA structure.
        NFA structure: {'Q': list, 'Σ': list, 'δ': dict, 'q0': str, 'F': list}
        """
        nfa_stack = []
        self._state_counter = 0 # Reset for each NFA construction

        # Helper to create a basic NFA for a symbol
        def create_basic_nfa(symbol):
            s0 = self._generate_state_name()
            s1 = self._generate_state_name()
            return {
                'Q': [s0, s1],
                'Σ': [symbol] if symbol != 'ε' else [],
                'δ': {(s0, symbol): {s1}},
                'q0': s0,
                'F': [s1]
            }

        for token in postfix:
            if token.isalnum() or token == 'ε':
                nfa_stack.append(create_basic_nfa(token))
            elif token == '.': # Concatenation
                if len(nfa_stack) < 2:
                    raise ValueError("Invalid postfix for concatenation")
                nfa2 = nfa_stack.pop()
                nfa1 = nfa_stack.pop()
                
                new_Q = nfa1['Q'] + nfa2['Q']
                new_Sigma = list(set(nfa1['Σ'] + nfa2['Σ']))
                new_delta = {**nfa1['δ'], **nfa2['δ']}
                # Add epsilon transition from accept states of nfa1 to start state of nfa2
                for f_state in nfa1['F']:
                    new_delta.setdefault((f_state, 'ε'), set()).add(nfa2['q0'])
                
                nfa_stack.append({
                    'Q': new_Q, 'Σ': new_Sigma, 'δ': new_delta,
                    'q0': nfa1['q0'], 'F': nfa2['F']
                })
            elif token == '|': # Union
                if len(nfa_stack) < 2:
                    raise ValueError("Invalid postfix for union")
                nfa2 = nfa_stack.pop()
                nfa1 = nfa_stack.pop()
                
                s_start = self._generate_state_name()
                s_end = self._generate_state_name()
                
                new_Q = nfa1['Q'] + nfa2['Q'] + [s_start, s_end]
                new_Sigma = list(set(nfa1['Σ'] + nfa2['Σ']))
                new_delta = {**nfa1['δ'], **nfa2['δ']}
                
                new_delta.setdefault((s_start, 'ε'), set()).update([nfa1['q0'], nfa2['q0']])
                for f_state in nfa1['F']:
                    new_delta.setdefault((f_state, 'ε'), set()).add(s_end)
                for f_state in nfa2['F']:
                    new_delta.setdefault((f_state, 'ε'), set()).add(s_end)
                
                nfa_stack.append({
                    'Q': new_Q, 'Σ': new_Sigma, 'δ': new_delta,
                    'q0': s_start, 'F': [s_end]
                })
            elif token == '*': # Kleene Star
                if len(nfa_stack) < 1:
                    raise ValueError("Invalid postfix for Kleene star")
                nfa1 = nfa_stack.pop()
                
                s_start = self._generate_state_name()
                s_end = self._generate_state_name()
                
                new_Q = nfa1['Q'] + [s_start, s_end]
                new_Sigma = nfa1['Σ'] # Alphabet remains same, epsilon transitions handle logic
                new_delta = {**nfa1['δ']}

                new_delta.setdefault((s_start, 'ε'), set()).update([nfa1['q0'], s_end])
                for f_state in nfa1['F']:
                    new_delta.setdefault((f_state, 'ε'), set()).update([nfa1['q0'], s_end])
                
                nfa_stack.append({
                    'Q': new_Q, 'Σ': new_Sigma, 'δ': new_delta,
                    'q0': s_start, 'F': [s_end]
                })
            else:
                raise ValueError(f"Unknown token in postfix expression: {token}")

        if len(nfa_stack) != 1:
            raise ValueError("Postfix expression did not result in a single NFA")
        
        final_nfa = nfa_stack[0]
        # Ensure all states are unique in Q, and Σ is also unique
        final_nfa['Q'] = list(set(final_nfa['Q']))
        final_nfa['Σ'] = list(set(final_nfa['Σ']))
        if 'ε' in final_nfa['Σ']: # NFA class handles epsilon internally if needed
            final_nfa['Σ'].remove('ε')
            
        return final_nfa

    def to_dfa(self):
        """Converts the regular expression to an equivalent DFA definition."""
        if not self.pattern: # Handle empty regex: accepts only empty string
             # This NFA accepts only the empty string.
            s0 = self._generate_state_name()
            nfa_structure = {'Q': [s0], 'Σ': [], 'δ': {}, 'q0': s0, 'F': [s0]}
        elif self.pattern == 'ε':
            s0 = self._generate_state_name()
            s1 = self._generate_state_name()
            nfa_structure = {'Q': [s0, s1], 'Σ': [], 'δ': {(s0, 'ε'): {s1}}, 'q0': s0, 'F': [s1]}
        else:
            infix_with_concat = self._add_concat_operator(self.pattern)
            postfix_regex = self._to_postfix(infix_with_concat)
            # print(f"DEBUG: Infix: {self.pattern} -> With Concat: {infix_with_concat} -> Postfix: {postfix_regex}")
            nfa_structure = self._postfix_to_nfa(postfix_regex)
            # print(f"DEBUG: NFA Structure from Postfix: {nfa_structure}")

        nfa_instance = NFA(nfa=nfa_structure)
        dfa_definition = nfa_instance.to_dfa()
        # print(f"DEBUG: DFA Definition: {dfa_definition}")
        return dfa_definition

    def visualize_dfa(self, input_string, index_dir='regex_sim_output'):
        """
        Generates and saves an HTML visualization of the DFA (derived from the regex)
        processing the input_string.
        """
        print(f"Processing regex: '{self.pattern}' for input string: '{input_string}'")
        try:
            dfa_definition = self.to_dfa()
        except Exception as e:
            print(f"Error during regex to DFA conversion: {e}")
            # Create a simple non-accepting DFA to avoid crashing visualization
            dfa_definition = {
                'Q': ['q_error_conversion'], 'Σ': list(set(c for c in self.pattern if c.isalnum())),
                'δ': {}, 'q0': 'q_error_conversion', 'F': []
            }
            for sym in dfa_definition['Σ']:
                dfa_definition['δ'][('q_error_conversion', sym)] = 'q_error_conversion'
            if not dfa_definition['Σ'] and self.pattern:
                 dfa_definition['Σ'] = ['#'] # Dummy symbol if alphabet is empty
                 dfa_definition['δ'][('q_error_conversion', '#')] = 'q_error_conversion'


        if not dfa_definition or not dfa_definition.get('Q') or not dfa_definition.get('q0'):
            print("Error: DFA definition is empty or malformed after to_dfa(). Cannot visualize.")
            # Fallback DFA
            dfa_definition = {
                'Q': ['q_error_viz'], 'Σ': list(set(c for c in self.pattern if c.isalnum())),
                'δ': {}, 'q0': 'q_error_viz', 'F': []
            }
            for sym in dfa_definition['Σ']:
                dfa_definition['δ'][('q_error_viz', sym)] = 'q_error_viz'
            if not dfa_definition['Σ'] and self.pattern :
                 dfa_definition['Σ'] = ['#'] 
                 dfa_definition['δ'][('q_error_viz', '#')] = 'q_error_viz'


        dfa_instance = DFA(dfa=dfa_definition)
        
        subtitle = f"DFA from Regex: '{self.pattern}'"
            
        return dfa_instance.visualization_video(
            input_string, 
            index_dir=index_dir,
        )

if __name__ == '__main__':
    # Test cases
    tests = [
        ("a", "a", "Simple char"),
        ("ab", "ab", "Concatenation"),
        ("a.b", "ab", "Explicit concatenation"),
        ("a|b", "a", "Union, match a"),
        ("a|b", "b", "Union, match b"),
        ("a*", "", "Kleene star, empty string"),
        ("a*", "a", "Kleene star, one a"),
        ("a*", "aaa", "Kleene star, multiple a's"),
        ("(a|b)*", "ababa", "Grouped union with star"),
        ("(a|b)*abb", "aabb", "Complex: (a|b)*abb"),
        ("(a|b)*abb", "abb", "Complex: (a|b)*abb, shorter match"),
        ("a(b|c)*d", "ad", "Complex: a(b|c)*d, no middle"),
        ("a(b|c)*d", "abd", "Complex: a(b|c)*d, one b"),
        ("a(b|c)*d", "acd", "Complex: a(b|c)*d, one c"),
        ("a(b|c)*d", "abccbd", "Complex: a(b|c)*d, multiple middle"),
        ("a(b|c)*d", "ac", "Complex: a(b|c)*d, non-match (incomplete)"),
        ("ε", "", "Epsilon regex"),
        ("a|ε", "a", "Char or Epsilon, match char"),
        ("a|ε", "", "Char or Epsilon, match epsilon"),
        ("aεb", "ab", "Concat with epsilon (should be like ab)"),
    ]

    for i, (regex_str, test_input, description) in enumerate(tests):
        print(f"--- Test Case {i+1}: {description} ---")
        print(f"Regex: '{regex_str}', Input: '{test_input}'")
        try:
            rgx = RegExp(regex_str)
            
            # Sanitize description for directory name
            # Replace any character that is not a word character, a period, or a hyphen with an underscore
            sanitized_description = re.sub(r'[^\\w.-]', '_', description)
            # Strip leading/trailing underscores, periods, or hyphens that might result from substitution
            sanitized_description = sanitized_description.strip('_.-') 
            # Limit length to avoid overly long paths
            if len(sanitized_description) > 50:
                sanitized_description = sanitized_description[:50]
            # Ensure it's not empty after sanitization, provide a default if it is
            if not sanitized_description:
                sanitized_description = "default_test_name"

            output_dir = f'regex_sim_output/test_{i+1}_{sanitized_description}'
            
            result = rgx.visualize_dfa(test_input, index_dir=output_dir)
            if result:
                print(f"  Input '{test_input}' accepted: {result['accepted']}")
                print(f"  Visualization HTML: {result['html_path']}")
            else:
                print(f"  Visualization failed or did not return result for {regex_str} with input {test_input}")
        except ValueError as e:
            print(f"  Error processing regex '{regex_str}': {e}")
        except Exception as e:
            import traceback
            print(f"  An unexpected error occurred processing regex '{regex_str}': {e}")
            print(traceback.format_exc())
        print("--- End Test Case ---")
