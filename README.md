# SpeakEase – Mental Health Assessment Tool

SpeakEase is a modern, web-based application designed to help users assess their mental health using the clinically validated PHQ-9 and GAD-7 questionnaires. Leveraging Google's Gemini AI, SpeakEase delivers personalized recommendations and interactive insights, all within a secure and user-friendly interface.

## Technology Stack

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Google Generative AI](https://img.shields.io/badge/Google%20Generative%20AI-Enabled-yellow?logo=google&logoColor=white)](https://ai.google/discover/generativeai/)
[![python-dotenv](https://img.shields.io/badge/dotenv-.env-green?logo=python&logoColor=white)](https://github.com/theskumar/python-dotenv)
[![HTML5](https://img.shields.io/badge/HTML5-Frontend-orange?logo=html5&logoColor=white)](https://developer.mozilla.org/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-Styling-blue?logo=css3&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6%2B-yellow?logo=javascript&logoColor=white)](https://developer.mozilla.org/docs/Web/JavaScript)
[![requirements.txt](https://img.shields.io/badge/Requirements-Txt-important?logo=python&logoColor=white)](requirements.txt)
[![.env](https://img.shields.io/badge/.env-Config-critical?logo=python&logoColor=white)](.env.example)
[![.gitignore](https://img.shields.io/badge/.gitignore-Git-orange?logo=git&logoColor=white)](https://git-scm.com/docs/gitignore)

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Important Notes](#important-notes)
- [Screenshots](#screenshots)

---

## Features

- **PHQ-9 Assessment:** 9-question depression screening based on clinical standards.
- **GAD-7 Assessment:** 7-question anxiety screening for generalized anxiety disorder.
- **AI-Powered Analysis:** Utilizes Google Gemini AI to interpret results and provide tailored feedback.
- **Personalized Recommendations:** 
  - Diet and lifestyle suggestions
  - Medication considerations (where appropriate)
- **Interactive Chat:** Engage with an AI assistant for follow-up questions regarding your results.
- **Professional UI:** Clean, responsive interface built with Bootstrap for an optimal user experience.

---

## Project Structure

```
speakease/
├── app.py                  # Main application script
├── requirements.txt        # Python dependencies
├── .env                   # User-specific environment variables (not tracked in VCS)
├── .env.example           # Example environment configuration
├── templates/
│   └── index.html         # Main HTML template
└── static/
    ├── css/
    │   └── style.css      # Custom styles
    └── js/
        └── app.js         # Client-side JavaScript
```

---

## Setup Instructions

### 1. Clone or Create the Project Directory

```bash
git clone https://github.com/CipJusCodin/Mental-Health-Assesment.git
cd Mental-Health-Assesment/speakease
```
*Alternatively, create the directory and structure manually if needed.*

### 2. Create the Directory Structure (if not cloned)

```bash
mkdir -p templates static/css static/js
```

### 3. Copy All Provided Files to Their Respective Locations

### 4. Create and Activate a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

- Copy `.env.example` to `.env`:
  ```bash
  cp .env.example .env
  ```
- Add your actual Google API key to the `.env` file:
  ```
  GOOGLE_API_KEY=your_actual_api_key_here
  ```

---

## Running the Application

1. **Ensure the virtual environment is activated.**
2. **Start the application:**
   ```bash
   python app.py
   ```
3. **The application will:**
   - Launch a local server on port 8000
   - Automatically open your default browser to [http://localhost:8000](http://localhost:8000)

---

## Usage

1. Complete the PHQ-9 and GAD-7 questionnaires.
2. Click **Submit Assessment** to generate your mental health report.
3. Review your personalized results and recommendations.
4. Use the interactive chat feature for further guidance or questions about your assessment.

---

## Troubleshooting

- **API Key Error:** Verify your Google API key is set correctly in the `.env` file.
- **Module Not Found:** Ensure all Python dependencies are installed via `pip install -r requirements.txt`.
- **Port Already in Use:** Default is port 8000. Change the port in `app.py` if necessary.

---

## Security

- **Never share your `.env` file or API key.**
- **Add `.env` to your `.gitignore` to prevent accidental exposure.**
- **This application is designed for local use. Exercise caution if deploying publicly.**

---

## Important Notes

- SpeakEase provides algorithmic assessments, not clinical diagnoses.
- Always consult a licensed healthcare professional for formal diagnosis or treatment.
- Protect your API keys and personal data.

---

## Screenshots

![Landing Page](https://github.com/user-attachments/assets/68168b3e-e650-4083-b4c0-e5d6f71523d1)
![Assessment Submission](https://github.com/user-attachments/assets/d146188f-8e17-48ea-91c4-ce97b897e9fe)
![Results Dashboard](https://github.com/user-attachments/assets/4aecc76c-0e21-4a02-a2a2-e94ef70e701e)
![Personalized Recommendations](https://github.com/user-attachments/assets/70ba1d62-bbb1-4177-9eeb-ced25c336847)
![Chat Feature](https://github.com/user-attachments/assets/eb4c6afb-35ab-4cfe-8e5c-0bacb9d98b06)

---

**Empowering individuals to take the first step towards better mental health – safely, privately, and intelligently.**
