import asyncio
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
if not GOOGLE_GEMINI_API_KEY:
    raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# ----------------------
# Channels (queues)
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
You are a data quality scanner. Look at the following CSV preview and identify potential issues:

{data_preview}
"""
    response = model.generate_content(prompt)
    await scan_channel.put(response.text)

async def rule_agent():
    scanner_output = await scan_channel.get()
    prompt = f"""
Generate quality checks in Python/pandas or SQL based on these issues. Provide only code:

{scanner_output}
"""
    response = model.generate_content(prompt)
    await rules_channel.put(response.text)

async def fix_agent():
    rules_output = await rules_channel.get()
    prompt = f"""
Generate Python/pandas or SQL code to fix these issues:

{rules_output}
"""
    response = model.generate_content(prompt)
    await fix_channel.put(response.text)

async def reporter_agent():
    fix_output = await fix_channel.get()
    # Also grab scanner output for report
    scanner_output = fix_output  # in MCP we can fetch it or chain messages
    prompt = f"""
Generate human-readable audit report for these issues and fixes:

Issues: {scanner_output}
Fixes applied: {fix_output}
"""
    response = model.generate_content(prompt)
    await report_channel.put(response.text)