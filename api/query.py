from http.server import BaseHTTPRequestHandler
import json
from services.assessment import answer_query

# In a production environment, you'd want to use a database or other persistent storage
# We'll need to store assessment results from the client instead since we can't rely on server-side state
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length
        content_length = int(self.headers['Content-Length'])
        # Read the POST data
        post_data = self.rfile.read(content_length)
        # Parse JSON data
        data = json.loads(post_data.decode('utf-8'))
        
        user_query = data.get('query', '')
        # Get assessment results from the client
        assessment_results = data.get('assessment_results', '')
        
        # Answer query
        answer = answer_query(user_query, assessment_results)
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Send response
        self.wfile.write(json.dumps({"answer": answer}).encode())
        return

    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        return