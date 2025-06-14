# DFA/NFA Visualization and Simulation Project

## Description

This project provides tools for defining, simulating, and visualizing Deterministic Finite Automata (DFA) and Nondeterministic Finite Automata (NFA). It can take automaton definitions from text files or interactive input, simulate their behavior on input strings, and generate animated HTML visualizations of the process. The DFA visualization also includes a table showing the binary encoding of each state.

## Features

*   **DFA and NFA Simulation:** Simulates the behavior of DFAs and NFAs on given input strings.
*   **Interactive Input:** Allows defining automata interactively through the command line.
*   **File Input:** Supports loading automaton definitions from `.txt` files.
*   **Animated Visualization:** Generates HTML-based animations showing the step-by-step processing of an input string by the automaton.
    *   Highlights the current state and active transitions.
    *   Shows the remaining input string.
    *   Indicates whether the string is accepted or rejected.
*   **State Encoding Table (DFA):** Displays a table mapping original state names to their binary encoded representations in the DFA visualization.
*   **NFA to DFA Conversion (Implied by `nfa_to_dfa_video_frames` folder):** The project structure suggests functionality for NFA to DFA conversion and its visualization. *(Please update this section if this feature is fully implemented and how to use it).*
*   **Regex Simulation (Implied by `regex.py` and `regex_sim_output` folder):** The project structure suggests functionality for regular expression simulation. *(Please update this section if this feature is fully implemented and how to use it).*

## File Structure

```
.
├── dfa.py                  # Core logic for DFA simulation and visualization
├── nfa.py                  # Core logic for NFA simulation and visualization (Assumed)
├── regex.py                # Logic for Regex simulation (Assumed)
├── dfa_input.txt           # Example input file for DFA definition
├── nfa_input.txt           # Example input file for NFA definition (Assumed)
├── dfa_video_frames/       # Output directory for DFA HTML visualizations
│   └── index.html
├── nfa_to_dfa_video_frames/ # Output directory for NFA to DFA conversion visualizations (Assumed)
│   └── index.html
├── regex_sim_output/       # Output directory for Regex simulation visualizations (Assumed)
│   └── ...
└── README.md               # This file
```

## Input File Format

The input files (e.g., `dfa_input.txt`) for defining automata follow this structure. Each section ends with a `#` character. Comments can be added using `//` at the beginning of a line.

1.  **States (Q):** Comma-separated list of state names.
    *   Example: `q0,q1,q2,q3#`
2.  **Alphabet (Σ):** Comma-separated list of input symbols.
    *   Example: `0,1#`
3.  **Transitions (δ):** Each transition on a new line in the format `current_state,input_symbol=new_state`.
    *   Example:
        ```
        q0,0=q1
        q0,1=q0
        q1,0=q2
        q1,1=q0#
        ```
4.  **Initial State (q0):** A single state name.
    *   Example: `q0#`
5.  **Accepting States (F):** Comma-separated list of accepting state names.
    *   Example: `q2#`

## How to Run

### DFA Simulation and Visualization

1.  Ensure Python and Graphviz are installed.
2.  Prepare your DFA definition in a file (e.g., `dfa_input.txt`) or be ready to input it interactively.
3.  Run the `dfa.py` script:
    ```bash
    python dfa.py
    ```
    The script will use `dfa_input.txt` by default (if `filename='dfa_input.txt'` is set in the main execution block) and process a predefined input string (e.g., `'10101'`).
4.  The HTML visualization will be saved in the `dfa_video_frames/` directory (or as specified in the script). Open `index.html` in a web browser to view the animation.

*(Add similar instructions for `nfa.py` and `regex.py` once their usage is finalized.)*

## Dependencies

*   **Python 3.x**
*   **Graphviz:**
    *   The `graphviz` Python library (`pip install graphviz`).
    *   Graphviz system installation (required for the `dot` command). Download from [graphviz.org](https://graphviz.org/download/). Ensure `dot` is in your system's PATH.

## Output

The primary output is an HTML file (`index.html`) containing an animated SVG visualization of the automaton processing an input string. This file is typically saved in a directory like `dfa_video_frames/`.

---

*This README is based on the observed project structure and functionality. Please update it with more specific details as the project evolves.*
