import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import json

# Load environment variables (for API key)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

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

# Store assessment results in memory
raw_assessment_results = ''

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

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/assessment', methods=['POST'])
def assessment():
    global raw_assessment_results
    
    # Parse the form data
    data = request.json
    
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
        raw_assessment_results = result['raw_assessment']
    
    # Return result
    return jsonify(result)

@app.route('/api/query', methods=['POST'])
def query():
    global raw_assessment_results
    
    # Parse the query
    data = request.json
    user_query = data.get('query', '')
    
    # Answer query
    answer = answer_query(user_query, raw_assessment_results)
    
    # Return result
    return jsonify({"answer": answer})

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY environment variable not set.")
        print("Please set it by running:")
        print("  On Windows: set GOOGLE_API_KEY=your_api_key_here")
        print("  On Linux/Mac: export GOOGLE_API_KEY=your_api_key_here")
        print("Or create a .env file with GOOGLE_API_KEY=your_api_key_here")
    
    # Run Flask app
    app.run(debug=True, port=8000)