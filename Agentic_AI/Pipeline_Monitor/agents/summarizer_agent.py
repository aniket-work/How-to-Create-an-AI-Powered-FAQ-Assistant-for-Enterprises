import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class SummarizerAgent:
    def summarize(self, event):
        if not event["error"]:
            return "No incident.", "No next steps", "Low"

        prompt = f"""
        You are a data engineering assistant.
        Summarize this incident for a data engineer,
        classify severity (High, Medium, Low), and suggest next steps:

        Pipeline: {event['pipeline']}
        Task ID: {event['task_id']}
        Error: {event['error']}
        """
        response = model.generate_content(prompt)
        content = response.text.strip()

        # Parse AI output for summary, next steps, severity
        # Expect format: Summary | Next Steps | Severity
        try:
            summary, next_steps, severity = [s.strip() for s in content.split("|")]
        except:
            summary = content
            next_steps = "Check logs and manual intervention"
            severity = "Medium"

        return summary, next_steps, severity