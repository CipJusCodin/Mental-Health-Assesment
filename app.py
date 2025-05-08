# app.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import http.server
import socketserver
import json
import urllib.parse
import threading
import webbrowser

# Load environment variables (for API key)
load_dotenv()

# Define your assessment prompt template
ASSESSMENT_PROMPT = """
You are a clinical assessment assistant analyzing mental health questionnaire data. Your task is to evaluate if the person shows signs of depression and provide specific recommendations.

FIRST, apply this specific algorithm to determine depression status:

1. Calculate the PHQ9 score (sum of all PHQ9 questions):
   - Question: "Little interest or pleasure in doing things?" Score: {phq1}
   - Question: "Feeling down, depressed, or hopeless?" Score: {phq2}
   - Question: "Trouble falling or staying asleep, or sleeping too much?" Score: {phq3}
   - Question: "Feeling tired or having little energy?" Score: {phq4}
   - Question: "Poor appetite or overeating?" Score: {phq5}
   - Question: "Feeling bad about yourself or that you are a failure?" Score: {phq6}
   - Question: "Trouble concentrating on things?" Score: {phq7}
   - Question: "Moving or speaking so slowly that others notice? Or being fidgety/restless?" Score: {phq8}
   - Question: "Thoughts that you would be better off dead or hurting yourself?" Score: {phq9}

2. Calculate GAD7 score (sum of all GAD7 questions):
   - Question: "Feeling nervous, anxious, or on edge?" Score: {gad1}
   - Question: "Not being able to stop or control worrying?" Score: {gad2}
   - Question: "Worrying too much about different things?" Score: {gad3}
   - Question: "Having trouble relaxing?" Score: {gad4}
   - Question: "Being so restless that it is hard to sit still?" Score: {gad5}
   - Question: "Becoming easily annoyed or irritable?" Score: {gad6}
   - Question: "Feeling afraid as if something awful might happen?" Score: {gad7}

3. Apply the standard PHQ9 scoring system:
   - 0-4 points: Not depressed
   - 5-9 points: Mildly depressed
   - 10-14 points: Moderately depressed
   - 15-19 points: Moderately severely depressed
   - 20-27 points: Severely depressed

4. Also check these critical indicators:
   - If score on "Feeling down, depressed, or hopeless?" is ≥ 2, increase depression likelihood
   - If score on "Little interest or pleasure in doing things?" is ≥ 2, increase depression likelihood
   - If score on suicidal thoughts question is ≥ 1, note as critical concern

5. Check GAD7 comorbidity - if GAD7 total score is ≥ 10, note anxiety complication

After completing this algorithmic assessment, provide ONLY the following information in this exact format:

1. DEPRESSION STATUS: State clearly if the patient is depressed or not depressed based on the algorithm results. If depressed, indicate severity (mild, moderate, moderately severe, or severe).

2. DIET RECOMMENDATIONS: List 3-5 specific dietary changes that could help improve their mental health.

3. LIFESTYLE RECOMMENDATIONS: List 3-5 specific lifestyle changes that could help improve their mental health.

4. MEDICATION CONSIDERATIONS: List 1-3 types of medications that might be considered (if appropriate) or state "No medication recommendations at this time" if not indicated.

5. IMPORTANT DISCLAIMER: Include the statement: "This is an algorithmic assessment only, not a clinical diagnosis. Please consult with a healthcare professional."

Keep your answer concise and strictly limited to these five sections only.
"""

QUERY_PROMPT = """
You are a mental health assistant helping interpret assessment results.
The assessment was analyzing PHQ9 (depression) and GAD7 (anxiety) questionnaire data.

The user has uploaded assessment data, and you have already analyzed it with these results:
{assessment_results}

Now the user is asking the following question:
{query}

IMPORTANT: First determine if this question is related to:
1. The mental health assessment
2. Mental health topics in general
3. Healthcare topics that might be relevant to the assessment

If the question is related to any of these categories, provide a helpful, concise response.
If the question is NOT related to these categories or is inappropriate, simply reply with "Invalid question. Please ask questions related to mental health or the assessment results."

Do NOT explain your determination process in your answer, just respond appropriately.
"""

# Initialize Gemini API
def initialize_gemini():
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return False, "Google API key not found"
        
        genai.configure(api_key=api_key)
        return True, "Gemini API initialized successfully"
    except Exception as e:
        return False, f"Error initializing Gemini API: {str(e)}"

# Run assessment
def run_assessment(phq_scores, gad_scores):
    try:
        # Initialize Gemini API
        success, message = initialize_gemini()
        if not success:
            return {"error": message}
        
        # Format the assessment prompt with scores
        formatted_prompt = ASSESSMENT_PROMPT.format(
            phq1=phq_scores.get("phq1", 0),
            phq2=phq_scores.get("phq2", 0),
            phq3=phq_scores.get("phq3", 0),
            phq4=phq_scores.get("phq4", 0),
            phq5=phq_scores.get("phq5", 0),
            phq6=phq_scores.get("phq6", 0),
            phq7=phq_scores.get("phq7", 0),
            phq8=phq_scores.get("phq8", 0),
            phq9=phq_scores.get("phq9", 0),
            gad1=gad_scores.get("gad1", 0),
            gad2=gad_scores.get("gad2", 0),
            gad3=gad_scores.get("gad3", 0),
            gad4=gad_scores.get("gad4", 0),
            gad5=gad_scores.get("gad5", 0),
            gad6=gad_scores.get("gad6", 0),
            gad7=gad_scores.get("gad7", 0)
        )
        
        # Use Gemini API to generate the assessment
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(formatted_prompt)
        
        # Extract the assessment result
        assessment_result = response.text
        
        # Parse results into sections
        sections = assessment_result.split("\n\n")
        
        result = {}
        
        for section in sections:
            if section.startswith("1. DEPRESSION STATUS:"):
                result["depression_status"] = section.replace("1. DEPRESSION STATUS:", "").strip()
            elif section.startswith("2. DIET RECOMMENDATIONS:"):
                diet_text = section.replace("2. DIET RECOMMENDATIONS:", "").strip()
                diet_items = [item.strip() for item in diet_text.split('\n')]
                result["diet_recommendations"] = diet_items
            elif section.startswith("3. LIFESTYLE RECOMMENDATIONS:"):
                lifestyle_text = section.replace("3. LIFESTYLE RECOMMENDATIONS:", "").strip()
                lifestyle_items = [item.strip() for item in lifestyle_text.split('\n')]
                result["lifestyle_recommendations"] = lifestyle_items
            elif section.startswith("4. MEDICATION CONSIDERATIONS:"):
                result["medication_considerations"] = section.replace("4. MEDICATION CONSIDERATIONS:", "").strip()
            elif section.startswith("5. IMPORTANT DISCLAIMER:"):
                result["disclaimer"] = section.replace("5. IMPORTANT DISCLAIMER:", "").strip()
        
        # Calculate raw scores for client
        result["phq9_score"] = sum(int(score) for score in phq_scores.values())
        result["gad7_score"] = sum(int(score) for score in gad_scores.values())
        
        # Store the raw assessment text for future queries
        result["raw_assessment"] = assessment_result
        
        return result
        
    except Exception as e:
        return {"error": f"Error generating assessment: {str(e)}"}

# Answer query
def answer_query(query, assessment_results):
    try:
        # Initialize Gemini API
        success, message = initialize_gemini()
        if not success:
            return f"Error: {message}"
        
        # Format the query prompt
        formatted_prompt = QUERY_PROMPT.format(
            assessment_results=assessment_results,
            query=query
        )
        
        # Use Gemini API to generate the response
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content(formatted_prompt)
        
        # Extract the answer
        answer = response.text
        
        return answer
        
    except Exception as e:
        return f"Error: {str(e)}"

# Create a custom HTTP request handler
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    # Store assessment results for the session
    raw_assessment_results = ''
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Set response headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/api/assessment':
            # Parse the form data
            data = json.loads(post_data)
            
            phq_scores = {}
            gad_scores = {}
            
            # Extract PHQ and GAD scores
            for key, value in data.items():
                if key.startswith('phq'):
                    phq_scores[key] = value
                elif key.startswith('gad'):
                    gad_scores[key] = value
            
            # Run assessment
            result = run_assessment(phq_scores, gad_scores)
            
            # Store raw assessment for future queries
            if 'raw_assessment' in result:
                CustomHandler.raw_assessment_results = result['raw_assessment']
            
            # Return result
            self.wfile.write(json.dumps(result).encode())
            
        elif self.path == '/api/query':
            # Parse the query
            data = json.loads(post_data)
            user_query = data.get('query', '')
            
            # Answer query
            answer = answer_query(user_query, CustomHandler.raw_assessment_results)
            
            # Return result
            self.wfile.write(json.dumps({"answer": answer}).encode())
            
        else:
            # Return error for unknown endpoints
            self.wfile.write(json.dumps({"error": "Unknown endpoint"}).encode())

# Define HTML content
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpeakEase - Mental Health Assessment</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #16A55A;
            --secondary-color: #1E2A3B;
            --light-bg: #f0f9f0;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }
        .navbar {
            background-color: var(--secondary-color);
            padding: 15px 0;
        }
        .navbar-brand {
            display: flex;
            align-items: center;
            color: white;
            font-weight: bold;
            font-size: 1.5rem;
        }
        .navbar-brand img {
            margin-right: 10px;
        }
        .navbar-nav .nav-link {
            color: white;
            margin: 0 10px;
        }
        .login-btn {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 5px;
        }
        .container {
            max-width: 800px;
            margin: 30px auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h2 {
            color: var(--primary-color);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e9ecef;
        }
        .assessment-section {
            background-color: var(--light-bg);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .question {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            background-color: #e9f5e9;
        }
        .options {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        .option {
            display: inline-flex;
            align-items: center;
            margin-right: 15px;
        }
        .option input {
            margin-right: 6px;
        }
        .nav-button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .assessment-title {
            color: var(--primary-color);
            font-weight: bold;
            font-size: 1.5rem;
            margin-bottom: 15px;
        }
        #results-container {
            display: none;
            margin-top: 30px;
        }
        .results-section {
            margin-bottom: 20px;
        }
        .results-section h3 {
            color: var(--primary-color);
            font-size: 1.3rem;
            margin-bottom: 10px;
        }
        .chat-container {
            margin-top: 30px;
            display: none;
        }
        .chat-messages {
            max-height: 300px;
            overflow-y: auto;
            margin-bottom: 15px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
        }
        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background-color: #e9f5e9;
            align-self: flex-end;
            margin-left: 20%;
        }
        .assistant-message {
            background-color: #e9ecef;
            align-self: flex-start;
            margin-right: 20%;
        }
        .loader {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        .loader-spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: var(--primary-color);
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        #error-message {
            display: none;
            color: red;
            margin-top: 20px;
            padding: 10px;
            background-color: #ffebee;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg">
        <div class="container-fluid">
            <a class="navbar-brand" href="#">
                <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect width="24" height="24" rx="5" fill="#16A55A"/>
                    <path d="M12 6C8.68629 6 6 8.68629 6 12C6 15.3137 8.68629 18 12 18C15.3137 18 18 15.3137 18 12C18 8.68629 15.3137 6 12 6Z" stroke="white" stroke-width="2"/>
                    <path d="M12 9V15M9 12H15" stroke="white" stroke-width="2"/>
                </svg>
                SpeakEase
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Services</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Pricing</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Testimonial</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#">Contact</a>
                    </li>
                </ul>
                <button class="login-btn ms-3">Login</button>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="container">
        <div id="assessment-container">
            <h2>Mental Health Assessment</h2>
            
            <!-- PHQ9 Assessment -->
            <div class="assessment-section">
                <div class="assessment-title">PHQ9 Assessment</div>
                
                <div class="question">
                    <div>Little interest or pleasure in doing things?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq1" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq1" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq1" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq1" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Feeling down, depressed, or hopeless?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq2" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq2" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq2" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq2" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Trouble falling or staying asleep, or sleeping too much?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq3" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq3" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq3" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq3" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Feeling tired or having little energy?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq4" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq4" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq4" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq4" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Poor appetite or overeating?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq5" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq5" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq5" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq5" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Feeling bad about yourself or that you are a failure?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq6" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq6" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq6" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq6" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Trouble concentrating on things?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq7" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq7" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq7" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq7" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Moving or speaking so slowly that others notice? Or being fidgety/restless?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq8" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq8" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq8" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq8" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Thoughts that you would be better off dead or hurting yourself?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="phq9" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="phq9" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq9" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="phq9" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
            </div>
            
            <!-- GAD7 Assessment -->
            <div class="assessment-section">
                <div class="assessment-title">GAD7 Assessment</div>
                
                <div class="question">
                    <div>Feeling nervous, anxious, or on edge?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad1" value="0"> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad1" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad1" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad1" value="3" checked> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Not being able to stop or control worrying?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad2" value="0"> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad2" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad2" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad2" value="3" checked> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Worrying too much about different things?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad3" value="0"> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad3" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad3" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad3" value="3" checked> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Having trouble relaxing?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad4" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad4" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad4" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad4" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Being so restless that it is hard to sit still?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad5" value="0"> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad5" value="1" checked> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad5" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad5" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Becoming easily annoyed or irritable?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad6" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad6" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad6" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad6" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
                
                <div class="question">
                    <div>Feeling afraid as if something awful might happen?</div>
                    <div class="options">
                        <label class="option">
                            <input type="radio" name="gad7" value="0" checked> 0 - Not at all
                        </label>
                        <label class="option">
                            <input type="radio" name="gad7" value="1"> 1 - Several days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad7" value="2"> 2 - More than half the days
                        </label>
                        <label class="option">
                            <input type="radio" name="gad7" value="3"> 3 - Nearly every day
                        </label>
                    </div>
                </div>
            </div>
            
            <div id="error-message"></div>
            <div class="loader" id="assessment-loader">
                <div class="loader-spinner"></div>
                <p>Analyzing your responses...</p>
            </div>
            
            <button id="submit-assessment" class="nav-button">Submit Assessment</button>
        </div>
        
        <!-- Results Container -->
        <div id="results-container">
            <h2>Assessment Results</h2>
            
            <div class="results-section">
                <h3>Depression Status</h3>
                <p id="depression-status"></p>
                <p id="assessment-scores"></p>
            </div>
            
            <div class="results-section">
                <h3>Diet Recommendations</h3>
                <ul id="diet-recommendations"></ul>
            </div>
            
            <div class="results-section">
                <h3>Lifestyle Recommendations</h3>
                <ul id="lifestyle-recommendations"></ul>
            </div>
            
            <div class="results-section">
                <h3>Medication Considerations</h3>
                <p id="medication-considerations"></p>
            </div>
            
            <div class="results-section">
                <h3>Disclaimer</h3>
                <p id="disclaimer"></p>
            </div>
            
            <!-- Chat Section -->
            <div class="chat-container" id="chat-container">
                <h3>Ask Questions About Your Assessment</h3>
                <p>You can ask questions about your assessment results or mental health in general.</p>
                
                <div class="chat-messages" id="chat-messages">
                    <!-- Messages will appear here -->
                </div>
                
                <div class="input-group mb-3">
                    <input type="text" class="form-control" id="chat-input" placeholder="Type your question...">
                    <button class="btn btn-success" type="button" id="send-message">Send</button>
                </div>
                <div class="loader" id="chat-loader">
                    <div class="loader-spinner"></div>
                    <p>Processing your question...</p>
                </div>
            </div>
            
            <button id="back-to-assessment" class="nav-button">Back to Assessment</button>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const submitAssessment = document.getElementById('submit-assessment');
            const backToAssessment = document.getElementById('back-to-assessment');
            const assessmentContainer = document.getElementById('assessment-container');
            const resultsContainer = document.getElementById('results-container');
            const chatContainer = document.getElementById('chat-container');
            const chatMessages = document.getElementById('chat-messages');
            const chatInput = document.getElementById('chat-input');
            const sendMessage = document.getElementById('send-message');
            const assessmentLoader = document.getElementById('assessment-loader');
            const chatLoader = document.getElementById('chat-loader');
            const errorMessage = document.getElementById('error-message');
            
            // Store assessment results
            let rawAssessmentResults = '';
            
            // Submit assessment
            submitAssessment.addEventListener('click', function() {
                // Show loader and hide error
                assessmentLoader.style.display = 'block';
                errorMessage.style.display = 'none';
                submitAssessment.disabled = true;
                
                // Collect all form data
                const formData = {};
                
                // Get PHQ9 scores
                for (let i = 1; i <= 9; i++) {
                    const selectedOption = document.querySelector(`input[name="phq${i}"]:checked`);
                    formData[`phq${i}`] = selectedOption ? selectedOption.value : "0";
                }
                
                // Get GAD7 scores
                for (let i = 1; i <= 7; i++) {
                    const selectedOption = document.querySelector(`input[name="gad${i}"]:checked`);
                    formData[`gad${i}`] = selectedOption ? selectedOption.value : "0";
                }
                
                // Send data to API
                fetch('/api/assessment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    // Hide loader
                    assessmentLoader.style.display = 'none';
                    submitAssessment.disabled = false;
                    
                    if (data.error) {
                        // Show error
                        errorMessage.textContent = data.error;
                        errorMessage.style.display = 'block';
                        return;
                    }
                    
                    // Store raw assessment for chat
                    rawAssessmentResults = data.raw_assessment || '';
                    
                    // Display results
                    document.getElementById('depression-status').textContent = data.depression_status || '';
                    document.getElementById('assessment-scores').textContent = 
                        `PHQ-9 Score: ${data.phq9_score || 0}, GAD-7 Score: ${data.gad7_score || 0}`;
                    
                    // Clear and populate lists
                    const dietList = document.getElementById('diet-recommendations');
                    dietList.innerHTML = '';
                    if (data.diet_recommendations && Array.isArray(data.diet_recommendations)) {
                        data.diet_recommendations.forEach(item => {
                            if (item && item.trim()) {
                                const li = document.createElement('li');
                                li.textContent = item;
                                dietList.appendChild(li);
                            }
                        });
                    }
                    
                    const lifestyleList = document.getElementById('lifestyle-recommendations');
                    lifestyleList.innerHTML = '';
                    if (data.lifestyle_recommendations && Array.isArray(data.lifestyle_recommendations)) {
                        data.lifestyle_recommendations.forEach(item => {
                            if (item && item.trim()) {
                                const li = document.createElement('li');
                                li.textContent = item;
                                lifestyleList.appendChild(li);
                            }
                        });
                    }
                    
                    document.getElementById('medication-considerations').textContent = data.medication_considerations || '';
                    document.getElementById('disclaimer').textContent = data.disclaimer || '';
                    
                    // Show results and chat
                    assessmentContainer.style.display = 'none';
                    resultsContainer.style.display = 'block';
                    chatContainer.style.display = 'block';
                })
                .catch(error => {
                    // Hide loader and show error
                    assessmentLoader.style.display = 'none';
                    submitAssessment.disabled = false;
                    errorMessage.textContent = "An error occurred. Please try again.";
                    errorMessage.style.display = 'block';
                    console.error('Error:', error);
                });
            });
            
            // Back to assessment
            backToAssessment.addEventListener('click', function() {
                resultsContainer.style.display = 'none';
                assessmentContainer.style.display = 'block';
                // Clear chat history
                chatMessages.innerHTML = '';
            });
            
            // Chat functionality
            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
                messageDiv.textContent = content;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function sendQuery(query) {
                // Show loader
                chatLoader.style.display = 'block';
                sendMessage.disabled = true;
                
                // Send query to API
                fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        assessment_results: rawAssessmentResults
                    })
                })
                .then(response => response.json())
                .then(data => {
                    // Hide loader
                    chatLoader.style.display = 'none';
                    sendMessage.disabled = false;
                    
                    if (data.error) {
                        addMessage("Error: " + data.error, false);
                        return;
                    }
                    
                    addMessage(data.answer, false);
                })
                .catch(error => {
                    // Hide loader
                    chatLoader.style.display = 'none';
                    sendMessage.disabled = false;
                    addMessage("Sorry, an error occurred. Please try again.", false);
                    console.error('Error:', error);
                });
            }
            
            // Send message button
            sendMessage.addEventListener('click', function() {
                const query = chatInput.value.trim();
                if (query) {
                    addMessage(query, true);
                    chatInput.value = '';
                    sendQuery(query);
                }
            });
            
            // Enter key in chat input
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    const query = chatInput.value.trim();
                    if (query) {
                        addMessage(query, true);
                        chatInput.value = '';
                        sendQuery(query);
                    }
                }
            });
        });
    </script>
</body>
</html>
"""

# Create a temporary index.html file
def create_html_file():
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

# Start server
def start_server(port=8000):
    create_html_file()
    handler = CustomHandler
    httpd = socketserver.TCPServer(("", port), handler)
    print(f"Server started at http://localhost:{port}")
    # Open browser automatically
    threading.Timer(1, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    httpd.serve_forever()

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        print("Please set it by running:")
        print("  On Windows: set GOOGLE_API_KEY=your_api_key_here")
        print("  On Linux/Mac: export GOOGLE_API_KEY=your_api_key_here")
        print("Or create a .env file with GOOGLE_API_KEY=your_api_key_here")
    
    # Start server
    start_server()