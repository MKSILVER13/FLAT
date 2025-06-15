# DFA/NFA/Regex Visualization and Simulation Project

## Description

This project provides tools for defining, simulating, and visualizing Deterministic Finite Automata (DFA), Nondeterministic Finite Automata (NFA), and Regular Expressions (Regex). It can take automaton/regex definitions from text files or interactive input, simulate their behavior on input strings, and generate animated HTML visualizations of the process.

## Setup and Running Instructions

### 1. Prerequisites
*   **Python 3.x:** Download from [python.org](https://www.python.org/).
*   **Graphviz (for visualizations):**
    *   **System Installation:** Download and install Graphviz from [graphviz.org/download/](https://graphviz.org/download/).
    *   **Add to PATH:** After installation, add the Graphviz `bin` directory to your system's PATH environment variable. This is crucial for the `dot` command to be accessible by the Python `graphviz` library.
        *   **Windows:** Search for "environment variables", click "Edit the system environment variables", then "Environment Variables...". Under "System variables", find "Path", select it, click "Edit...", "New", and add the path to your Graphviz `bin` folder (e.g., `C:\\\\Program Files\\\\Graphviz\\\\bin`).
        *   **macOS/Linux:** Edit your shell's configuration file (e.g., `.bashrc`, `.zshrc`) to add `export PATH="/path/to/graphviz/bin:$PATH"`. Replace `/path/to/graphviz/bin` with the actual path.

### 2. Clone the Repository (Optional)
If you haven't already, clone the project repository:
```bash
git clone <repository_url>
cd <repository_directory>
```

### 3. Set up a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows
venv\\\\Scripts\\\\activate
# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
Install the required Python libraries, including `graphviz` (Python wrapper) and `Flask` (for the server), by running:
```bash
pip install -r requirements.txt
```
If `requirements.txt` is not present or exhaustive, you might need to install key packages manually:
```bash
pip install graphviz flask
```

### 5. Running the Scripts

*   **DFA Simulation & Visualization:**
    ```powershell
    python dfa.py <optional_dfa_input_file.txt> <optional_input_string>
    ```
    Defaults to `dfa_input.txt` and string `'10101'`. Output: `dfa_video_frames/index.html`.

*   **NFA Simulation & Visualization (and NFA to DFA conversion):**
    ```powershell
    python nfa.py <optional_nfa_input_file.txt> <optional_input_string>
    ```
    Defaults to `nfa_input.txt` and a predefined string. Outputs: `nfa_simulation_output/index.html` (simulation) and `nfa_to_dfa_video_frames/index.html` (conversion).

*   **Regex Simulation & Visualization:**
    ```powershell
    python regex.py "<your_regex_pattern>" "<your_input_string>" <optional_test_name>
    ```
    Example: `python regex.py "(a|b)*abb" "aabbabb" test_run`
    Output: `regex_sim_output/<test_name>/index.html`.

*   **Running the Web Server:**
    ```powershell
    python server.py
    ```
    Starts a Flask server, typically at `http://127.0.0.1:5000`.

## Project Overview

### Core Concepts
*   **DFA (Deterministic Finite Automaton):** A state machine where each state has exactly one transition for each input symbol.
*   **NFA (Nondeterministic Finite Automaton):** A state machine that can have multiple transitions for an input symbol or transitions on an empty string (epsilon).
*   **Regex (Regular Expression):** A sequence of characters defining a search pattern, often visualized by conversion to an NFA/DFA.

### Key Features
*   Simulation of DFAs, NFAs, and Regex.
*   Interactive command-line input or file-based definitions.
*   Animated HTML/SVG visualizations of step-by-step processing.
*   NFA to DFA conversion and visualization.
*   A web interface (`server.py`) for easier interaction.
*   DFA visualizations include a state-to-binary encoding table.

### Input File Format for Automata
Automata definitions (e.g., `dfa_input.txt`) use sections ending with `#`:
1.  **States (Q):** `q0,q1,q2#`
2.  **Alphabet (Σ):** `0,1#`
3.  **Transitions (δ):** `current_state,input_symbol=new_state` (one per line, section ends with `#`)
4.  **Initial State (q0):** `q0#`
5.  **Accepting States (F):** `q2#`
Comments can be added using `//` at the start of a line.

### Output
The scripts primarily generate `index.html` files within specific directories (e.g., `dfa_video_frames/`, `nfa_to_dfa_video_frames/`, `regex_sim_output/`). These files contain the animated SVG visualizations.

### File Structure
\`\`\`
.
├── dfa.py                  # DFA logic
├── nfa.py                  # NFA logic (incl. conversion)
├── regex.py                # Regex logic
├── server.py               # Web server (Flask)
├── requirements.txt        # Dependencies
├── *.txt                   # Example input files
├── */index.html            # Output visualization files
└── README.md               # This file
\`\`\`

---

*This README provides a general overview. Refer to individual script comments or code for more specific details.*
