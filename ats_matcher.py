import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

with open("my_resume.txt", "r") as f:
    resume = f.read()

with open("job_description.txt", "r") as f:
    jd = f.read()

prompt = f"""
You are an expert Applicant Tracking System (ATS) and technical recruiter.
Compare the following Resume against the Job Description.

Provide:
1. An ATS Match Score (0-100%).
2. Missing Keywords (skills or tools in the JD that are missing from the resume).
3. 3 specific, honest ways to rewrite the resume bullets to match the JD without inventing fake experience.

--- RESUME ---
{resume}

--- JOB DESCRIPTION ---
{jd}
"""

print("Analyzing your resume against the job description...\n")
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt,
)
print(response.text)
