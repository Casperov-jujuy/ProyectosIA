import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Test the exact same prompt structure used in main.py
prompt = """
You are an expert ATS Resume Optimizer.
Target Job: "Software Engineer"

Resume content:
"John Doe, Software Developer with 5 years of experience in Python and JavaScript."

Task: Rewrite experience bullets to be action-oriented and ATS-friendly for the target job.
Output: Strictly a JSON object (no markdown) with keys: name, contact_info, education, experience, skills.
"""

try:
    print("Testing gemini-2.5-flash with sample prompt...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    print("SUCCESS! Response received:")
    print(response.text[:500])  # Print first 500 chars
except Exception as e:
    print(f"FAILED: {e}")
