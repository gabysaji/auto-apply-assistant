import os
import re
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fpdf import FPDF

load_dotenv()
client = genai.Client()

with open("my_resume.txt", "r") as f:
    base_resume = f.read()

jobs = pd.read_csv("jobs.csv")
os.makedirs("applications", exist_ok=True)
tracker_rows = []

def clean(text):
    return str(text).encode("latin-1", "replace").decode("latin-1").strip()

def save_pdf(data, filepath):
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def write_block(text, h=5):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w=pdf.epw, h=h, text=clean(text), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(w=pdf.epw, h=8, text=clean(data.get("name", "")), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=pdf.epw, h=5, text=clean(data.get("contact", "")), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    def header(title):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(20, 50, 90)
        pdf.cell(w=pdf.epw, h=6, text=clean(title.upper()), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(20, 50, 90)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    if data.get("summary"):
        header("Professional Summary")
        pdf.set_font("Helvetica", "", 10)
        write_block(data["summary"])
        pdf.ln(3)

    if data.get("skills"):
        header("Technical Skills")
        pdf.set_font("Helvetica", "", 10)
        for s in data["skills"]:
            write_block(s)
        pdf.ln(3)

    if data.get("experience"):
        header("Experience")
        for exp in data["experience"]:
            pdf.set_font("Helvetica", "B", 10.5)
            write_block(exp.get("title", ""), h=5.5)
            pdf.set_font("Helvetica", "", 10)
            for b in exp.get("bullets", []):
                write_block(f"  - {b}")
            pdf.ln(2)

    if data.get("projects"):
        header("Projects")
        for proj in data["projects"]:
            pdf.set_font("Helvetica", "B", 10.5)
            write_block(proj.get("title", ""), h=5.5)
            pdf.set_font("Helvetica", "", 10)
            for b in proj.get("bullets", []):
                write_block(f"  - {b}")
            pdf.ln(2)

    if data.get("education"):
        header("Education")
        pdf.set_font("Helvetica", "", 10)
        write_block(data["education"])

    pdf.output(filepath)

print(f"Processing {len(jobs)} jobs from jobs.csv...\n")

for idx, row in jobs.head(3).iterrows():
    title = str(row.get("title", "Role"))
    company = str(row.get("company", "Company"))
    url = str(row.get("job_url", ""))
    jd = str(row.get("description", ""))

    if not jd or jd == "nan":
        print(f"Skipping {title} at {company} (no description found).")
        continue

    print(f"[{idx + 1}] Analyzing: {title} at {company}...")
    prompt = f"""
    Compare this Resume against the Job Description. Never invent fake experience or tools.
    Return ONLY valid JSON:
    {{
      "ats_score": 75,
      "cover_note": "3-sentence human message to the recruiter explaining fit",
      "tailored_resume": {{
        "name": "Full Name",
        "contact": "City, Country | Phone | Email | LinkedIn",
        "summary": "2-3 sentence tailored summary",
        "skills": ["Category: skill1, skill2"],
        "experience": [{{"title": "Role | Company | Location | Dates", "bullets": ["Bullet 1"]}}],
        "projects": [{{"title": "Project | Tools", "bullets": ["Bullet 1"]}}],
        "education": "Degree | University | Year"
      }}
    }}
    --- RESUME ---
    {base_resume}
    --- JOB DESCRIPTION ---
    {jd[:4000]}
    """

    res = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    result = json.loads(res.text)
    score = result.get("ats_score", 0)
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", f"{company}_{title}")[:40]
    folder = os.path.join("applications", safe_name)
    os.makedirs(folder, exist_ok=True)

    pdf_path = os.path.join(folder, f"Resume_{safe_name}.pdf")
    save_pdf(result["tailored_resume"], pdf_path)

    with open(os.path.join(folder, "cover_note.txt"), "w") as cf:
        cf.write(result.get("cover_note", ""))

    tracker_rows.append({
        "Company": company,
        "Role": title,
        "ATS_Score": score,
        "Resume_PDF": pdf_path,
        "Apply_URL": url,
        "Status": "Ready to Submit"
    })
    print(f"    -> ATS Score: {score}% | Saved packet in {folder}/\n")

pd.DataFrame(tracker_rows).to_csv("tracker.csv", index=False)
print("All done! Open tracker.csv or the 'applications' folder to review and submit.")
