# SpeakEase - Mental Health Assessment Tool

A web-based mental health assessment tool that uses PHQ-9 and GAD-7 questionnaires to evaluate depression and anxiety levels, providing personalized recommendations.

## Project Structure

```
speakease/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Example environment file
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── css/
    │   └── style.css      # Styling
    └── js/
        └── app.js         # Frontend JavaScript
```

## Setup Instructions

1. **Clone or create the project directory:**
   ```bash
   mkdir speakease
   cd speakease
   ```

2. **Create the directory structure:**
   ```bash
   mkdir -p templates static/css static/js
   ```

3. **Copy all the provided files to their respective locations**

4. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Google API key to the `.env` file:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```

## Running the Application

1. **Make sure your virtual environment is activated**

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **The application will:**
   - Start a local server on port 8000
   - Automatically open your default browser
   - Navigate to http://localhost:8000

## Features

- **PHQ-9 Assessment:** 9-question depression screening
- **GAD-7 Assessment:** 7-question anxiety screening
- **AI-Powered Analysis:** Uses Google's Gemini AI for assessment
- **Personalized Recommendations:**
  - Diet recommendations
  - Lifestyle recommendations
  - Medication considerations (when appropriate)
- **Interactive Chat:** Ask follow-up questions about your assessment
- **Professional UI:** Clean, responsive design with Bootstrap

## Usage

1. Fill out the PHQ-9 and GAD-7 questionnaires
2. Click "Submit Assessment"
3. Review your results and recommendations
4. Use the chat feature to ask questions about your assessment

## Important Notes

- This tool provides algorithmic assessments only, not clinical diagnoses
- Always consult with a healthcare professional for proper diagnosis and treatment
- Keep your API key secure and never commit it to version control

## Troubleshooting

If you encounter issues:

1. **API Key Error:** Make sure your Google API key is correctly set in the `.env` file
2. **Module Not Found:** Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **Port Already in Use:** The default port is 8000. If it's in use, modify the port in `app.py`

## Security

- Never share your `.env` file or API key
- The `.env` file should be added to `.gitignore` if using version control
- This is a local application - be cautious if deploying to production

![WhatsApp Image 2025-06-20 at 2 56 17 PM](https://github.com/user-attachments/assets/68168b3e-e650-4083-b4c0-e5d6f71523d1)
![WhatsApp Image 2025-06-20 at 2 56 17 PM (1)](https://github.com/user-attachments/assets/d146188f-8e17-48ea-91c4-ce97b897e9fe)
![WhatsApp Image 2025-06-20 at 2 56 17 PM (2)](https://github.com/user-attachments/assets/4aecc76c-0e21-4a02-a2a2-e94ef70e701e)
![WhatsApp Image 2025-06-20 at 2 56 18 PM](https://github.com/user-attachments/assets/70ba1d62-bbb1-4177-9eeb-ced25c336847)
![WhatsApp Image 2025-06-20 at 2 56 16 PM](https://github.com/user-attachments/assets/eb4c6afb-35ab-4cfe-8e5c-0bacb9d98b06)

