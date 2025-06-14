class DFA:
    def __init__(self, dfa=None, filename=None):
        if dfa is not None:
            self.dfa = dfa
            self.current_state = dfa['q0']
            self.accepting_states = set(dfa['F'])
            self.transition_functions = dfa['δ']
            self.states = set(dfa['Q'])
            self.input_alphabet = set(dfa['Σ'])
            self.path = []
        else:
            self.dfa = self.take_dfa(filename=filename)
        self.current_state = self.dfa['q0']
        self.accepting_states = set(self.dfa['F'])
        self.transition_functions = self.dfa['δ']
        self.states = set(self.dfa['Q'])
        self.input_alphabet = set(self.dfa['Σ'])
        self.path = []
        self.max_intensity = 3
        
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
    def print(self):
        print("DFA Description:")
        print(f"States (Q): {self.states}")
        print(f"Input Alphabet (Σ): {self.input_alphabet}")
        print(f"Transition Function (δ): {self.transition_functions}")
        print(f"Initial State (q0): {self.current_state}")
        print(f"Accepting States (F): {self.accepting_states}")
    
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

    def _dfa_svg_frame(self, state, node_intensity, path, idx):
        from graphviz import Digraph
        dot = Digraph(format='svg')
        dot.attr(rankdir='LR', bgcolor='white')
        for s in self.states:
            if s in self.accepting_states:
                shape = 'doublecircle'
            else:
                shape = 'circle'
            intensity = node_intensity[s]
            if s == state:
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
            dot.node(s, shape=shape, color=color, style=style, fontcolor=fontcolor, fontsize='18')
        dot.node('start', shape='point', color='white')
        dot.edge('start', self.dfa['q0'], color='blue', penwidth='2')
        # Edge coloring by intensity
        for (src, symbol), dst in self.transition_functions.items():
            intensity = self.edge_intensity.get((src, symbol), 0)
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
            dot.edge(src, dst, label=symbol, color=color, penwidth=penwidth, fontcolor=fontcolor, fontsize='16')
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
        html = (
            '<html>\n'
            '<head>\n'
            '    <meta charset="utf-8">\n'
            '    <title>DFA/NFA Visualization Animation</title>\n'
            '    <style>\n'
            '        body {{ background: #222; color: #eee; font-family: sans-serif; }}\n'
            '        #svgbox {{ width: 80vw; height: 60vh; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px #0003; display: block; margin: 0 auto; overflow: auto; }}\n'
            '        .controls {{ margin: 1em 0; text-align: center; }}\n'
            '        .inputvis {{ text-align: center; margin: 1em 0 0.5em 0; }}\n'
            '        .accept {{ color: #4caf50; font-weight: bold; }}\n'
            '        .reject {{ color: #e53935; font-weight: bold; }}\n'
            '        span {{ font-size: 1.2em; }}\n'
            '        h1 {{ text-align: center; font-size: 1.5em; }}\n'
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
            '</html>'
        ).format(
            len(svg_frames),
            svg_frames[0],
            input_visuals[0],
            'accept' if accepted else 'reject',
            "ACCEPTED" if accepted else "REJECTED",
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
        initial_id = (self.dfa['q0'], in_string)
        self.ids.append(initial_id)
        possible_ids = [initial_id]
        svg_frames = []
        input_visuals = []
        node_intensity = {s: 0 for s in self.states}
        accept_found = False
        accept_state = None
        while possible_ids:
            # Check for accept
            for state, rem in possible_ids:
                if rem == '' and state in self.accepting_states:
                    accept_found = True
                    accept_state = state
                    break
            if accept_found:
                break
            # Update node and edge intensity for all current possible states and edges
            for s in node_intensity:
                if node_intensity[s] > 0:
                    node_intensity[s] -= 1
            for k in self.edge_intensity:
                if self.edge_intensity[k] > 0:
                    self.edge_intensity[k] -= 1
            for state, rem in possible_ids:
                node_intensity[state] = self.max_intensity
            # Visualize all current possible states
            svg_frames.append(self._dfa_svg_frame(possible_ids[0][0], node_intensity, [pid[0] for pid in possible_ids], 0))
            input_visuals.append(self._dfa_input_visuals(possible_ids))
            # Step
            next_possible_ids = self._dfa_run(possible_ids)
            prev_ids = possible_ids
            possible_ids = next_possible_ids
        accepted = accept_found
        # Final frame for accept/reject
        svg_frames.append(self._dfa_svg_frame(accept_state if accept_found else svg_frames[-1], node_intensity, [pid[0] for pid in possible_ids], 0))
        input_visuals.append(self._dfa_input_visuals(prev_ids))
        html = self._dfa_html(svg_frames, input_visuals, accepted, [pid[0] for pid in possible_ids])
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
        index_path = os.path.join(index_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return {'html_path': index_path, 'accepted': accepted, 'path': self.ids}


__main__ = '__main__'
if __name__ == '__main__':
    dfa = DFA(filename='dfa_input.txt')
    dfa.visualization_video('10101', index_dir='dfa_video_frames')
