from http.server import BaseHTTPRequestHandler
import json
from services.assessment import run_assessment

# Store assessment results for the session 
# Note: This is ephemeral storage that won't persist between function invocations
# In a production environment, you'd want to use a database or other persistent storage
assessment_results = ""

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length
        content_length = int(self.headers['Content-Length'])
        # Read the POST data
        post_data = self.rfile.read(content_length)
        # Parse JSON data
        data = json.loads(post_data.decode('utf-8'))
        
        # Extract PHQ and GAD scores
        phq_scores = {}
        gad_scores = {}
        
        for key, value in data.items():
            if key.startswith('phq'):
                phq_scores[key] = value
            elif key.startswith('gad'):
                gad_scores[key] = value
        
        # Run assessment
        result = run_assessment(phq_scores, gad_scores)
        
        # Store raw assessment for future queries (note: this won't persist between function invocations)
        global assessment_results
        if 'raw_assessment' in result:
            assessment_results = result['raw_assessment']
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Send response
        self.wfile.write(json.dumps(result).encode())
        return

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return