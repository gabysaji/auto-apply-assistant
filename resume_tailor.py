import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fpdf import FPDF

load_dotenv()
client = genai.Client()

with open("my_resume.txt", "r") as f:
    resume = f.read()

with open("job_description.txt", "r") as f:
    jd = f.read()

prompt = f"""
You are an expert ATS resume writer. Tailor the resume below to strongly match the job description without inventing fake experience, tools, or jobs.
Return ONLY valid JSON matching this exact structure:
{{
  "name": "Full Name",
  "contact": "City, Country | Phone | Email | LinkedIn",
  "summary": "2-3 sentence tailored professional summary",
  "skills": ["Category: skill1, skill2", "Category: skill3, skill4"],
  "experience": [
    {{
      "title": "Job Title | Company | Location | Dates",
      "bullets": ["Action verb + task + measurable impact", "Bullet 2"]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name | Tools Used",
      "bullets": ["Bullet 1"]
    }}
  ],
  "education": "Degree | University | Year"
}}

--- RESUME ---
{resume}

--- JOB DESCRIPTION ---
{jd}
"""

print("Tailoring and formatting your resume...")
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
    ),
)

data = json.loads(response.text)

def clean(text):
    return str(text).encode("latin-1", "replace").decode("latin-1").strip()

pdf = FPDF()
pdf.set_margins(15, 15, 15)
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

def write_block(text, h=5):
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(w=pdf.epw, h=h, text=clean(text), new_x="LMARGIN", new_y="NEXT")

# Header: Name & Contact
pdf.set_font("Helvetica", "B", 18)
pdf.cell(w=pdf.epw, h=8, text=clean(data.get("name", "")), align="C", new_x="LMARGIN", new_y="NEXT")

pdf.set_font("Helvetica", "", 9.5)
pdf.set_text_color(80, 80, 80)
pdf.cell(w=pdf.epw, h=5, text=clean(data.get("contact", "")), align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(4)

def add_section_header(title):
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(20, 50, 90)
    pdf.cell(w=pdf.epw, h=6, text=clean(title.upper()), new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(20, 50, 90)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

# Summary
if data.get("summary"):
    add_section_header("Professional Summary")
    pdf.set_font("Helvetica", "", 10)
    write_block(data["summary"], h=5)
    pdf.ln(3)

# Skills
if data.get("skills"):
    add_section_header("Technical Skills")
    pdf.set_font("Helvetica", "", 10)
    for skill in data["skills"]:
        write_block(skill, h=5)
    pdf.ln(3)

# Experience
if data.get("experience"):
    add_section_header("Experience")
    for exp in data["experience"]:
        pdf.set_font("Helvetica", "B", 10.5)
        write_block(exp.get("title", ""), h=5.5)
        pdf.set_font("Helvetica", "", 10)
        for b in exp.get("bullets", []):
            write_block(f"  - {b}", h=5)
        pdf.ln(2)

# Projects
if data.get("projects"):
    add_section_header("Projects")
    for proj in data["projects"]:
        pdf.set_font("Helvetica", "B", 10.5)
        write_block(proj.get("title", ""), h=5.5)
        pdf.set_font("Helvetica", "", 10)
        for b in proj.get("bullets", []):
            write_block(f"  - {b}", h=5)
        pdf.ln(2)

# Education
if data.get("education"):
    add_section_header("Education")
    pdf.set_font("Helvetica", "", 10)
    write_block(data["education"], h=5)

output_file = "tailored_resume.pdf"
pdf.output(output_file)
print(f"Done! Saved clean formatted PDF to {output_file}")
