from flask import Flask, render_template, request, session
import pandas as pd
import asyncio
import os
import google.generativeai as genai
from dotenv import load_dotenv

# ----------------------
# Load environment variables
# ----------------------
load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("Please set GOOGLE_GEMINI_API_KEY in .env or environment variables")

genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ----------------------
# Flask config
# ----------------------
app = Flask(__name__)
app.secret_key = "super-secret-key"  # For session storage

# ----------------------
# MCP-style channels
# ----------------------
scan_channel = asyncio.Queue()
rules_channel = asyncio.Queue()
fix_channel = asyncio.Queue()
report_channel = asyncio.Queue()

# ----------------------
# Agent definitions
# ----------------------
async def scanner_agent(data_preview):
    prompt = f"""
You are a data quality scanner. Look at the following CSV preview and identify potential issues like missing values, duplicates, or outliers:

{data_preview}
"""
    response = model.generate_content(prompt)
    await scan_channel.put(response.text)

async def rule_agent():
    scanner_output = await scan_channel.get()
    prompt = f"""
Generate quality checks in Python/pandas or SQL based on these issues. Provide only the code.

{scanner_output}
"""
    response = model.generate_content(prompt)
    await rules_channel.put((scanner_output, response.text))  # pass scanner_output for later

async def fix_agent():
    scanner_output, rules_output = await rules_channel.get()
    prompt = f"""
Generate Python/pandas or SQL code to automatically fix these issues:

{rules_output}
"""
    response = model.generate_content(prompt)
    await fix_channel.put((scanner_output, rules_output, response.text))

async def reporter_agent():
    scanner_output, rules_output, fixes_output = await fix_channel.get()
    prompt = f"""
Generate a concise, human-readable audit report based on the detected issues and the fixes applied:

Issues: {scanner_output}
Fixes applied: {fixes_output}
"""
    response = model.generate_content(prompt)
    await report_channel.put((scanner_output, rules_output, fixes_output, response.text))

# ----------------------
# Flask routes
# ----------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Upload CSV
        file = request.files["data_file"]
        df = pd.read_csv(file)
        preview_text = df.head(5).to_csv(index=False)

        # Store preview in session
        session["original_preview"] = df.head(5).to_dict(orient="records")

        # Trigger MCP agents asynchronously
        async def run_agents():
            await asyncio.gather(
                scanner_agent(preview_text),
                rule_agent(),
                fix_agent(),
                reporter_agent()
            )
            scanner_out, rules_out, fixes_out, audit_report = await report_channel.get()

            # Store all outputs in session
            session["fixed_preview"] = df.head(5).to_dict(orient="records")
            session["fixes_code"] = fixes_out
            session["audit_report"] = audit_report

        asyncio.run(run_agents())

        return render_template(
            "report.html",
            original_preview=session["original_preview"],
            fixed_preview=session["fixed_preview"],
            fixes_code=session["fixes_code"],
            audit_report=session["audit_report"],
            db_choice=request.form["db_choice"]
        )

    return render_template("index.html")


@app.route("/apply_fixes", methods=["POST"])
def apply_fixes():
    data = request.json
    db_choice = data.get("db_choice")
    # Currently session-only demo; could integrate real DB logic here
    return {"status": f"Fixes applied to {db_choice} (session-only demo)"}


if __name__ == "__main__":
    app.run(debug=True, port=5001)