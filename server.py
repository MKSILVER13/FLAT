import http.server
import socketserver
import json
import os
import sys
import tempfile
import webbrowser
import urllib.parse
from pathlib import Path
from threading import Timer

# Import the automata classes
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dfa import DFA
from nfa import NFA
from regex import RegExp

# Port for the web server
PORT = 8000

# Directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class AutomataRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve static files
        if self.path == '/':
            self.path = '/frontend.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        # Process form submissions
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        response = {'success': False, 'message': 'Unknown error', 'path': None}
        
        if self.path == '/api/process_dfa':
            response = self.handle_dfa(data)
        elif self.path == '/api/process_nfa':
            response = self.handle_nfa(data)
        elif self.path == '/api/process_regex':
            response = self.handle_regex(data)
          # Send response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Send response content
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def handle_dfa(self, data):
        try:
            input_string = data.get('inputString', '')
            
            # Check if using file input or manual input
            if 'filename' in data:
                filename = data['filename']
                # If filename is provided but doesn't exist, fall back to default
                if not os.path.exists(filename):
                    filename = 'dfa_input.txt'
                dfa = DFA(filename=filename)
            elif 'manual' in data:
                # Create temporary file with manual input
                manual_data = data['manual']
                temp_file = self.create_temp_dfa_file(manual_data)
                dfa = DFA(filename=temp_file)
                # Clean up temp file
                os.remove(temp_file)
            else:
                return {'success': False, 'message': 'No DFA definition provided'}
            
            # Process the DFA
            try:
                result = dfa.visualization_video(input_string, index_dir='dfa_video_frames')
            except FileNotFoundError as e:
                if 'dot' in str(e) or 'Graphviz' in str(e):
                    return {
                        'success': False,
                        'message': "Graphviz not found. Please install Graphviz and make sure it's in your PATH. See README for installation instructions."
                    }
                raise
                
            return {
                'success': True, 
                'message': f"DFA processed successfully. String {'accepted' if result['accepted'] else 'rejected'}.",
                'path': result['html_path'],
                'accepted': result['accepted']            }
        except Exception as e:
            return {'success': False, 'message': f"Error processing DFA: {str(e)}"}
    
    def handle_nfa(self, data):
        try:
            input_string = data.get('inputString', '')
            
            # Check if using file input or manual input
            if 'filename' in data:
                filename = data['filename']
                # If filename is provided but doesn't exist, fall back to default
                if not os.path.exists(filename):
                    filename = 'nfa_input.txt'
                nfa = NFA(filename=filename)
            elif 'manual' in data:
                # Create temporary file with manual input
                manual_data = data['manual']
                temp_file = self.create_temp_nfa_file(manual_data)
                nfa = NFA(filename=temp_file)
                # Clean up temp file
                os.remove(temp_file)
            else:
                return {'success': False, 'message': 'No NFA definition provided'}
            
            # Process the NFA
            try:
                result = nfa.visualize_dfa_equivalent(input_string, index_dir='nfa_to_dfa_video_frames')
            except FileNotFoundError as e:
                if 'dot' in str(e) or 'Graphviz' in str(e):
                    return {
                        'success': False,
                        'message': "Graphviz not found. Please install Graphviz and make sure it's in your PATH. See README for installation instructions."
                    }
                raise
                
            return {
                'success': True, 
                'message': f"NFA processed successfully. String {'accepted' if result['accepted'] else 'rejected'}.",
                'path': result['html_path'],
                'accepted': result['accepted']
            }
        except Exception as e:
            return {'success': False, 'message': f"Error processing NFA: {str(e)}"}
    def handle_regex(self, data):
        try:
            pattern = data.get('pattern', '')
            input_string = data.get('inputString', '')
            
            # Create sanitized directory name from pattern
            import re
            safe_pattern = re.sub(r'[^a-zA-Z0-9]', '_', pattern)
            if len(safe_pattern) > 30:
                safe_pattern = safe_pattern[:30]
            
            dir_name = f"regex_sim_output/run_{safe_pattern}"
            
            # Process the regex
            regex = RegExp(pattern)
            
            try:
                result = regex.visualize_dfa(input_string, index_dir=dir_name)
            except FileNotFoundError as e:
                if 'dot' in str(e) or 'Graphviz' in str(e):
                    return {
                        'success': False,
                        'message': "Graphviz not found. Please install Graphviz and make sure it's in your PATH. See README for installation instructions."
                    }
                raise
            
            return {
                'success': True, 
                'message': f"Regex processed successfully. String {'accepted' if result['accepted'] else 'rejected'}.",
                'path': result['html_path'],
                'accepted': result['accepted']
            }
        except Exception as e:
            return {'success': False, 'message': f"Error processing Regex: {str(e)}"}
    
    def create_temp_dfa_file(self, manual_data):
        """Create a temporary file with DFA definition"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp:
            # Write states (Q)
            temp.write(manual_data['states'] + '#\n')
            # Write alphabet (Σ)
            temp.write(manual_data['alphabet'] + '#\n')
            # Write transitions (δ)
            transitions = manual_data['transitions'].strip().split('\n')
            for transition in transitions:
                temp.write(transition + '\n')
            temp.write('#\n')
            # Write initial state (q0)
            temp.write(manual_data['initial'] + '#\n')
            # Write accepting states (F)
            temp.write(manual_data['accepting'] + '#\n')
            
            return temp.name
    
    def create_temp_nfa_file(self, manual_data):
        """Create a temporary file with NFA definition"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp:
            # Write states (Q)
            temp.write(manual_data['states'] + '#\n')
            # Write alphabet (Σ)
            temp.write(manual_data['alphabet'] + '#\n')
            # Write transitions (δ)
            transitions = manual_data['transitions'].strip().split('\n')
            for transition in transitions:
                temp.write(transition + '\n')
            temp.write('#\n')
            # Write initial state (q0)
            temp.write(manual_data['initial'] + '#\n')
            # Write accepting states (F)            temp.write(manual_data['accepting'] + '#\n')
            
            return temp.name


def open_browser():
    """Open browser after short delay"""
    webbrowser.open(f'http://localhost:{PORT}/')

if __name__ == '__main__':
    # Change to the directory where this script is located
    os.chdir(BASE_DIR)
    
    # Create a web server
    handler = AutomataRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Serving at http://localhost:{PORT}/")
    print("Press Ctrl+C to stop the server")
    
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    
    try:
        # Start the server
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()
