# Mental-Health-Assesment
# SpeakEase - Mental Health Assessment

SpeakEase is a web application that provides mental health assessments using standardized questionnaires (PHQ-9 for depression and GAD-7 for anxiety) and Google's Gemini AI model to analyze the results and provide recommendations.

## Features

- PHQ-9 depression assessment
- GAD-7 anxiety assessment 
- AI-powered analysis of results
- Personalized recommendations for diet and lifestyle changes
- Interactive chat to ask questions about the assessment results

## Deployment on Vercel

This application is structured to be deployed on Vercel, using serverless functions to handle the API requests.

### Environment Variables

You need to set up the following environment variable in your Vercel project:

- `GOOGLE_API_KEY`: Your Google Gemini API key

### Deployment Steps

1. Fork or clone this repository
2. Sign up for [Vercel](https://vercel.com) if you haven't already
3. Connect your GitHub repository to Vercel
4. Add the required environment variables
5. Deploy the project

## Local Development

### Prerequisites

- Python 3.7 or higher
- A Google Gemini API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/speakease.git
   cd speakease
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

4. For local development, you can use the Vercel CLI:
   ```
   npm install -g vercel
   vercel dev
   ```

## Project Structure

```
speakease/
├── .env                       # Environment variables (local development only)
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── vercel.json                # Vercel configuration
├── api/                       # Serverless API functions
│   ├── __init__.py           
│   ├── assessment.py          # Assessment API endpoint
│   └── query.py               # Query API endpoint
├── services/
│   ├── __init__.py            
│   └── assessment.py          # Assessment logic and Gemini API integration
└── public/                    # Static files
    ├── index.html             # Main HTML page
    ├── css/
    │   └── styles.css         # CSS styles
    └── js/
        └── main.js            # JavaScript for client-side functionality
```

## Disclaimer

This application provides algorithmic assessments only, not clinical diagnoses. It should not be used as a substitute for professional mental health evaluation or treatment. Please consult with a healthcare professional for proper diagnosis and treatment.

## License

[MIT License](LICENSE)