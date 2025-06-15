import math  # Add math import for ceil and log2 if needed, or use bit_length
import sys # Add sys import for command-line arguments

class DFA:
    def __init__(self, dfa=None, filename=None):
        if dfa is not None:
            self.dfa_def = dfa # Store the definition
            # self.current_state = dfa['q0'] # Initial current_state is set from dfa_def later
            # self.accepting_states = set(dfa['F'])
            # self.transition_functions = dfa['δ']
            # self.states = set(dfa['Q'])
            # self.input_alphabet = set(dfa['Σ'])
            # self.path = []
        else:
            self.dfa_def = self.take_dfa(filename=filename) # dfa_def is a dictionary
        
        self.states = set(self.dfa_def['Q'])
        self.input_alphabet = set(self.dfa_def['Σ'])
        self.transition_functions = self.dfa_def['δ']
        self.initial_state = self.dfa_def['q0'] # Use a consistent name
        self.accepting_states = set(self.dfa_def['F'])
        
        self.current_state = self.initial_state # Set current_state for simulation
        self.path = []
        self.max_intensity = 3

        # Generate state encodings
        self.state_encoding = {}
        self.state_decoding = {} # Optional: for debugging or if needed later
        
        sorted_states = sorted(list(self.states))
        if not sorted_states:
            num_bits = 0
        elif len(sorted_states) == 1:
            num_bits = 1 # Represent single state as '0'
        else:
            num_bits = (len(sorted_states) - 1).bit_length()

        for i, state_name in enumerate(sorted_states):
            encoded_name = format(i, f'0{num_bits}b') if num_bits > 0 else '0' # handle num_bits=0 for single state
            if not sorted_states and not num_bits: # if there are no states
                 encoded_name = "ERROR_NO_STATES" # Should not happen with valid DFA
            self.state_encoding[state_name] = encoded_name
            self.state_decoding[encoded_name] = state_name
        
    def take_dfa(self, filename=None):
        """
        Reads DFA description from a file if filename is provided, otherwise uses interactive input.
        File format (dfa_input.txt):
        - States (Q): comma-separated, ends with #
        - Alphabet (Σ): comma-separated, ends with #
        - Transitions: each as current_state,input_symbol=new_state per line, ends with #
        - Initial state: single line, ends with #
        - Accepting states: comma-separated, ends with #
        """
        if filename:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('//')]
            # Find indices of lines ending with '#'
            section_indices = [i for i, line in enumerate(lines) if line.endswith('#')]
            if len(section_indices) < 5:
                raise ValueError('DFA input file format is incorrect or incomplete.')
            # Parse sections
            Q = [state.strip() for state in lines[0].replace('#','').split(',') if state.strip()]
            sigma = [alphabet.strip() for alphabet in lines[1].replace('#','').split(',') if alphabet.strip()]
            # Transitions: lines 2 to section_indices[2]
            delta = {}
            for i in range(2, section_indices[2]+1):
                line = lines[i].replace('#','').strip()
                if not line:
                    continue
                key, value = line.split('=')
                current_state, input_symbol = [x.strip() for x in key.split(',')]
                delta[(current_state, input_symbol)] = value.strip()
            q0 = lines[section_indices[3]].replace('#','').strip()
            F = [state.strip() for state in lines[section_indices[4]].replace('#','').split(',') if state.strip()]
            return {
                'Q': Q,
                'Σ': sigma,
                'δ': delta,
                'q0': q0,
                'F': F
            }
        print("Description of DFA format: (Q, Σ, δ, q0, F)")
        Q = input("Enter the set of states(Q) (comma_separated): ").split(',')
        Q = [state.strip() for state in Q]

        Sigma = input("Enter the input alphabet(Σ) (comma-separated): ").split(',')
        sigma = [alphabet.strip() for alphabet in Sigma]



        print("Enter the transition function δ:")
        print("Format: current_state,input_symbol=new_state (Enter 'done' to stop)")
        delta = {}
        while True:
            entry = input("δ: ")
            if entry.lower() == 'done':
                break
            try:
                key, value = entry.split('=')
                if(value.strip() not in Q):
                    continue
                current_state, input_symbol = key.split(',')
                if(current_state.strip() not in Q or input_symbol.strip() not in sigma):
                    continue
                if((current_state.strip(), input_symbol.strip()) in delta):
                    print(f"Transition for ({current_state.strip()}, {input_symbol.strip()}) already exists. Overwriting.")
                    print("if you are trying to build NFA, please use a different option.")
                delta[(current_state.strip(), input_symbol.strip())] = value.strip()
            except:
                print("Invalid format. Try again.")
            
        def take_q0():        
            q0 = input("Enter the initial state: ").strip()
            if q0 not in Q:
                print(f"Initial state {q0} is not in the set of states {Q}. Please try again.")
                q0 = take_q0()
            return q0

        F = input("Enter the set of accepting states (comma-separated): ").split(',')
        F = [state.strip() for state in F]
        for state in F:
            if state not in Q:
                F.remove(state)

        return {
                'Q': Q,
                'Σ': sigma,
                'δ': delta,
                'q0': take_q0(),
                'F': F
            }
    def print_dfa(self):
        print("DFA Description:")
        print(f"States (Q): {self.states}")
        print(f"Input Alphabet (Σ): {self.input_alphabet}")
        print(f"Transition Function (δ): {self.transition_functions}")
        print(f"Initial State (q0): {self.initial_state}") # Changed from self.current_state
        print(f"Accepting States (F): {self.accepting_states}")
        if hasattr(self, 'state_encoding') and self.state_encoding:
            print("State Encodings:")
            for original, encoded in self.state_encoding.items():
                print(f"  {original} -> {encoded}")
    
    def _dfa_step(self, current_state, symbol):
        """Return the next state for a given state and symbol, or None if invalid."""
        return self.transition_functions.get((current_state, symbol))

    def _dfa_run(self, prev_possible_ids):
        """Given a list of (state, remaining_string), return next possible ids (no repeats), and update edge intensities."""
        next_possible_ids = []
        for state, rem in prev_possible_ids:
            if not rem:
                continue  # No more symbols to process for this id
            symbol = rem[0]
            next_state = self._dfa_step(state, symbol)
            if next_state is not None:
                new_id = (next_state, rem[1:])
                if new_id not in self.ids:
                    self.ids.append(new_id)
                    next_possible_ids.append(new_id)
                # Update edge intensity
                if (state, symbol) in self.edge_intensity:
                    self.edge_intensity[(state, symbol)] = self.max_intensity+1
        return next_possible_ids

    def _dfa_svg_frame(self, current_processing_state_original, node_intensity, path_original_states, idx):
        from graphviz import Digraph
        dot = Digraph(format='svg')
        dot.attr(rankdir='LR', bgcolor='white')

        # Use encoded names for nodes
        for s_orig in self.states:
            s_encoded = self.state_encoding.get(s_orig, str(s_orig)) # Fallback to original if not found
            
            if s_orig in self.accepting_states:
                shape = 'doublecircle'
            else:
                shape = 'circle'
            
            intensity = node_intensity[s_orig] # Intensity is keyed by original state name
            
            # Highlighting based on the original name of the current processing state
            if s_orig == current_processing_state_original:
                color = '#ffd700'  # gold for current state
                fontcolor = 'black'
                style = 'filled,bold'
            elif intensity > 0:
                if intensity == self.max_intensity:
                    color = "#1e88e5"  # vivid blue
                elif intensity == self.max_intensity-1:
                    color = "#64b5f6"  # lighter blue
                elif intensity == self.max_intensity-2:
                    color = "#bbdefb"  # pale blue
                fontcolor = 'black'
                style = 'filled'
            else:
                color = 'lightgray'
                fontcolor = 'black'
                style = ''
            # Node label can be the original name or the encoded one. Let's use encoded for compactness.
            # If original name is desired on the node, use s_orig as label.
            dot.node(s_encoded, label=s_encoded, shape=shape, color=color, style=style, fontcolor=fontcolor, fontsize='18')

        if self.initial_state in self.state_encoding: # Check if initial_state is encodable
            encoded_initial_state = self.state_encoding[self.initial_state]
            dot.node('start', shape='point', color='white') # Keep 'start' node as is
            dot.edge('start', encoded_initial_state, color='blue', penwidth='2')
        
        # Edge coloring by intensity, using encoded state names for src/dst
        for (src_orig, symbol), dst_orig in self.transition_functions.items():
            src_encoded = self.state_encoding.get(src_orig, str(src_orig))
            dst_encoded = self.state_encoding.get(dst_orig, str(dst_orig))
            
            intensity = self.edge_intensity.get((src_orig, symbol), 0) # Intensity keyed by original
            if intensity == self.max_intensity:
                color = '#b71c1c'  # dark red
            elif intensity == self.max_intensity-1:
                color = '#e53935'  # red
            elif intensity == self.max_intensity-2:
                color = '#ffcdd2'  # light red
            else:
                color = 'black'
            penwidth = '3' if intensity > 0 else '1'
            fontcolor = 'red' if intensity > 0 else 'black'
            dot.edge(src_encoded, dst_encoded, label=symbol, color=color, penwidth=penwidth, fontcolor=fontcolor, fontsize='16')
            
        return dot.pipe().decode('utf-8')

    def _dfa_input_visuals(self, possible_ids):
        visuals = []
        for state, rem in possible_ids:
            processed_len = self.input_length - len(rem)
            chars = []
            for i, ch in enumerate(self.input_string):
                if i < processed_len:
                    chars.append('<span style="color:purple;font-weight:bold;">{}</span>'.format(ch))
                elif i == processed_len:
                    chars.append('<span style="color:gold;font-weight:bold; border:2px solid gold; border-radius:50%; padding:2px 8px; margin:0 2px; background:#222;">{}</span>'.format(ch))
                else:
                    chars.append('<span style="color:black;">{}</span>'.format(ch))
            visuals.append(
                f"<div style='display:inline-block; margin:0.5em 1em; padding:0.4em 1.2em; background:linear-gradient(90deg,#1e88e5 60%,#bbdefb 100%); border-radius:2em; box-shadow:0 2px 8px #0002;'>"
                f"<span style='background:#fff; color:#1e88e5; font-weight:bold; border-radius:1em; padding:0.2em 1em; font-size:1.2em; margin-right:0.8em; border:2px solid #1e88e5; box-shadow:0 1px 4px #0001;'>State: <b>{state}</b></span>"
                f"<span style='font-size:1.3em;letter-spacing:0.2em;'>{''.join(chars)}</span>"
                f"</div>"
            )
        return '<br/>'.join(visuals)
        
    def _dfa_html(self, svg_frames, input_visuals, accepted, path):
        accepted_str = "ACCEPTED" if accepted else "REJECTED"
        
        # Generate encoding table rows
        encoding_table_rows = ""
        for encoded, original in sorted(self.state_decoding.items()):
            encoding_table_rows += f"<tr><td>{encoded}</td><td>{original}</td></tr>\n"
        
        html = (
            '<html>\n'
            '<head>\n'
            '    <meta charset="utf-8">\n'
            '    <title>DFA/NFA Visualization Animation</title>\n'
            '    <style>\n'
            '        body {{ background: #222; color: #eee; font-family: sans-serif; }}\n'
            '        #svgbox {{ width: 80vw; height: 60vh; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #0003; display: block; margin: 0 auto; overflow: auto; }}\n'
            '        #encoding-table {{ width: 80vw; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #0003; margin: 20px auto; overflow: auto; color: #333; padding: 15px; }}\n'
            '        .controls {{ margin: 1em 0; text-align: center; }}\n'
            '        .inputvis {{ text-align: center; margin: 1em 0 0.5em 0; }}\n'
            '        .accept {{ color: #4caf50; font-weight: bold; }}\n'
            '        .reject {{ color: #e53935; font-weight: bold; }}\n'
            '        span {{ font-size: 1.2em; }}\n'
            '        h1, h2 {{ text-align: center; }}\n'
            '        h1 {{ font-size: 1.5em; }}\n'
            '        h2 {{ font-size: 1.2em; margin-top: 0; color: #333; }}\n'
            '        table {{ width: 100%; border-collapse: collapse; }}\n'
            '        th, td {{ padding: 8px; text-align: center; border-bottom: 1px solid #333; }}\n'
            '        th {{ background-color: #4caf50; color: white; }}\n'
            '        td {{ color: #333; font-weight: bold; }}\n'
            '        tr:hover {{ background-color: #f5f5f5; }}\n'
            '    </style>\n'
            '</head>\n'
            '<body>\n'
            '    <h1>DFA/NFA Visualization Animation</h1>\n'
            '    <div class="controls">\n'
            '        <span>Step <span id="step">1</span> / <span id="total">{}</span></span>\n'
            '    </div>\n'
            '    <div id="svgbox">{}</div>\n'
            '    <div class="inputvis" id="inputvis">{}</div>\n'
            '    <div class="controls" id="result" style="display:none;">\n'
            '        <span class="{}">String {} by Machine</span>\n'
            '    </div>\n'
            '    <div id="encoding-table">\n'
            '        <h2>State Encodings</h2>\n'
            '        <table>\n'
            '            <tr><th>Binary Code</th><th>State Name</th></tr>\n'
            '            {}\n'
            '        </table>\n'
            '    </div>\n'
            '    <script>\n'
            '        const frames = [\n{}\n        ];\n'
            '        const inputVisuals = [\n{}\n        ];\n'
            '        const total = frames.length;\n'
            '        let current = 0;\n'
            '        document.getElementById("total").textContent = total;\n'
            '        function showFrame(idx) {{\n'
            '            document.getElementById("svgbox").innerHTML = frames[idx];\n'
            '            document.getElementById("step").textContent = idx+1;\n'
            '            document.getElementById("inputvis").innerHTML = inputVisuals[idx];\n'
            '            if(idx === total-1) {{\n'
            '                document.getElementById("result").style.display = "";\n'
            '            }} else {{\n'
            '                document.getElementById("result").style.display = "none";\n'
            '            }}\n'
            '        }}\n'
            '        function autoPlay() {{\n'
            '            showFrame(current);\n'
            '            current++;\n'
            '            if (current >= total) {{\n'
            '                setTimeout(() => {{ current = 0; showFrame(current); autoPlay(); }}, 3000);\n'
            '            }} else {{\n'
            '                setTimeout(autoPlay, 1000);\n'
            '            }}\n'
            '        }}\n'
            '        autoPlay();\n'
            '    </script>\n'
            '</body>\n'
            '</html>'        ).format(
            len(svg_frames),
            svg_frames[0],
            input_visuals[0],
            'accept' if accepted else 'reject',
            "ACCEPTED" if accepted else "REJECTED",
            encoding_table_rows,  # Place encoding table rows here
            ',\n'.join([repr(s) for s in svg_frames]),
            ',\n'.join([repr(s) for s in input_visuals])
        )
        return html

    def visualization_video(self, in_string, index_dir='dfa_video_frames', delay=1.0, embed_in_index=True):
        import os
        self.ids = []
        self.input_string = in_string
        self.input_length = len(in_string)
        self.edge_intensity = {(src, symbol): 0 for (src, symbol) in self.transition_functions}
        
        # Initial ID uses the original initial state name
        initial_id = (self.initial_state, in_string)
        self.ids.append(initial_id)
        
        possible_ids = [initial_id] # Contains original state names
        svg_frames = []
        input_visuals = []
        node_intensity = {s: 0 for s in self.states} # Keyed by original state names
        accept_found = False
        accept_state_original = None # Store original name of accepting state
        
        prev_ids = [] # Contains original state names

        while possible_ids:
            # Check for accept using original state names
            for state_orig, rem in possible_ids:
                if rem == '' and state_orig in self.accepting_states:
                    accept_found = True
                    accept_state_original = state_orig
                    break
            if accept_found:
                break
            
            # Update node and edge intensity (keyed by original names)
            for s_orig_intensity in node_intensity:
                if node_intensity[s_orig_intensity] > 0:
                    node_intensity[s_orig_intensity] -= 1
            for k_orig_intensity in self.edge_intensity:
                if self.edge_intensity[k_orig_intensity] > 0:
                    self.edge_intensity[k_orig_intensity] -= 1
            for state_orig, rem in possible_ids:
                node_intensity[state_orig] = self.max_intensity
            
            # Determine current state for SVG frame (original name)
            current_display_state_original = possible_ids[0][0] if possible_ids else self.initial_state
            
            # Generate SVG frame: pass original state name for highlighting logic
            # path argument to _dfa_svg_frame is [pid[0] for pid in possible_ids] - these are original names
            svg_frames.append(self._dfa_svg_frame(current_display_state_original, node_intensity, [pid[0] for pid in possible_ids], len(svg_frames)))
            input_visuals.append(self._dfa_input_visuals(possible_ids)) # Uses original names for display
            
            # Step (uses original names internally)
            next_possible_ids = self._dfa_run(possible_ids)
            prev_ids = possible_ids
            possible_ids = next_possible_ids
        accepted = accept_found
        
        # Final frame for accept/reject
        # Determine final display state (original name)
        final_display_state_original = self.initial_state # Default
        if accepted and accept_state_original:
            final_display_state_original = accept_state_original
        elif prev_ids: # If not accepted but there were previous states
            final_display_state_original = prev_ids[0][0]
        
        # Update node_intensity for the final frame (keyed by original names)
        if accepted and accept_state_original:
            node_intensity[accept_state_original] = self.max_intensity
        elif final_display_state_original in node_intensity : # Check if it's a valid state
             node_intensity[final_display_state_original] = self.max_intensity


        # Path for the final frame (original names)
        final_frame_path_originals = [pid[0] for pid in prev_ids if prev_ids] if not accepted else [accept_state_original] if accept_state_original else []

        svg_frames.append(self._dfa_svg_frame(final_display_state_original, node_intensity, final_frame_path_originals, len(svg_frames)))
        
        # Input visuals for the final frame
        # If accepted, the input is fully processed. If rejected, it's the state of prev_ids.
        final_input_visual_ids = prev_ids if not accepted and prev_ids else [(accept_state_original, '')] if accepted and accept_state_original else [(final_display_state_original, '')] if not prev_ids and not possible_ids else possible_ids

        input_visuals.append(self._dfa_input_visuals(final_input_visual_ids)) 
        
        html = self._dfa_html(svg_frames, input_visuals, accepted, [pid[0] for pid in self.ids]) # path for html can be original
        
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
        index_path = os.path.join(index_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return {'html_path': index_path, 'accepted': accepted, 'path': self.ids} # self.ids contains original state names


if __name__ == '__main__':
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        input_string = sys.argv[2]
        dfa = DFA(filename=filename)
        dfa.visualization_video(input_string, index_dir='dfa_video_frames')
    elif len(sys.argv) == 2:
        input_string = sys.argv[1]
        dfa = DFA(filename='dfa_input.txt')
        dfa.visualization_video(input_string, index_dir='dfa_video_frames')
    elif len(sys.argv) == 1:
        # Default behavior if no arguments are provided
        dfa = DFA(filename='dfa_input.txt')
        dfa.visualization_video('10101', index_dir='dfa_video_frames')
    else:
        print("Usage: python dfa.py <filename> <input_string>")
        print("Or: python dfa.py (to use default dfa_input.txt and string '10101')")
