# SPIRIT AI

A responsive Flask-based personal AI assistant based on the uploaded **SPIRIT AI — First Code** PDF.

## Features
- AI chat using the OpenAI Responses API
- Optional web search tool for AI answers
- Voice input in supported browsers (Web Speech API)
- Spoken AI replies (browser speech synthesis)
- Local `/time`, `/date`, `/calc`, `/search`, and `/help` commands
- Responsive dark interface for desktop and mobile
- API key kept on the server, not in browser code

## Requirements
- Python 3.10+
- An OpenAI API key with API access and billing configured
- Internet connection

## Setup

1. Extract the ZIP.
2. Open a terminal in the `spirit_ai` folder.
3. Create and activate a virtual environment (recommended):

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Set your API key as an environment variable. Do not share it or put it in frontend files.

   **Windows PowerShell**
   ```powershell
   $env:OPENAI_API_KEY="your-api-key"
   ```

   **macOS / Linux**
   ```bash
   export OPENAI_API_KEY="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"
   ```

6. Start the app:
   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.

## Configuration
- `OPENAI_API_KEY`: required for AI answers.
- `OPENAI_MODEL`: optional model name; defaults to `gpt-5.5` to match the supplied starter code. Change it to a model enabled for your API account if needed.
- `PORT`: optional local server port; defaults to `5000`.

## Commands
- `/time`
- `/date`
- `/calc (25 + 5) * 3`
- `/search weather in Hyderabad`
- `/help`

## Notes
- This is a runnable starter application, not a hosted public app. You need to run it on your computer or deploy it to a server.
- API usage may incur charges according to your OpenAI API account.
- Browser voice input support varies. Chrome-based browsers generally offer the best support.
- For public deployment, use HTTPS, add authentication and rate limiting, and run behind a production WSGI server (for example, Waitress or Gunicorn). Do not use Flask's development server for production.
