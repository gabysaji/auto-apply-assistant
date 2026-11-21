import os
import re
import time
import json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fpdf import FPDF

load_dotenv()
client = genai.Client(http_options={"timeout": 15000})

LINKEDIN_URL = "https://www.linkedin.com/in/gabysaji"
GITHUB_URL = "https://github.com/gabysaji"
MODELS = ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-3.8-flash"]
MIN_SCORE = 70
MAX_JOBS = 25

with open("my_resume.txt", "r") as f:
    base_resume = f.read()

seen_file = "seen_jobs.txt"
seen_urls = set()
if os.path.exists(seen_file):
    with open(seen_file, "r") as sf:
        seen_urls = set(line.strip() for line in sf if line.strip())

raw_jobs = pd.read_csv("jobs.csv")
jobs = raw_jobs[~raw_jobs["job_url"].isin(seen_urls)].head(MAX_JOBS)
os.makedirs("applications", exist_ok=True)
tracker_rows = []

def clean(text):
    return str(text).encode("latin-1", "replace").decode("latin-1").strip()

def render_with_scale(data, scale):
    pdf = FPDF()
    margin = 12 * scale
    pdf.set_margins(12, margin, 12)
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    body_font = 9.5 * scale
    line_h = 4.6 * scale
    sec_gap = 2.8 * scale

    def write_block(text, h=line_h):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w=pdf.epw, h=h, text=clean(text), new_x="LMARGIN", new_y="NEXT")

    # Name Header
    pdf.set_font("Helvetica", "B", 17 * scale)
    pdf.cell(w=pdf.epw, h=7.5 * scale, text=clean(data.get("name", "GABY SAJI")), align="C", new_x="LMARGIN", new_y="NEXT")

    # Contact Line + Clickable LinkedIn & GitHub
    pdf.set_font("Helvetica", "", 9.2 * scale)
    pdf.set_text_color(60, 60, 60)
    contact_base = clean(data.get("contact", "Kerala, India | (+91) 9447518866 | gabysajithomas@outlook.com"))
    base_w = pdf.get_string_width(contact_base + " | ")
    li_w = pdf.get_string_width("LinkedIn")
    sep_w = pdf.get_string_width(" | ")
    gh_w = pdf.get_string_width("GitHub")
    total_w = base_w + li_w + sep_w + gh_w

    pdf.set_x((pdf.w - total_w) / 2)
    pdf.cell(w=base_w, h=5 * scale, text=contact_base + " | ")
    pdf.set_text_color(15, 80, 160)
    pdf.set_font("Helvetica", "U", 9.2 * scale)
    pdf.cell(w=li_w, h=5 * scale, text="LinkedIn", link=LINKEDIN_URL)
    pdf.set_text_color(60, 60, 60)
    pdf.set_font("Helvetica", "", 9.2 * scale)
    pdf.cell(w=sep_w, h=5 * scale, text=" | ")
    pdf.set_text_color(15, 80, 160)
    pdf.set_font("Helvetica", "U", 9.2 * scale)
    pdf.cell(w=gh_w, h=5 * scale, text="GitHub", link=GITHUB_URL, new_x="LMARGIN", new_y="NEXT")

    # Availability Line
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "I", 8.8 * scale)
    pdf.cell(w=pdf.epw, h=4.8 * scale, text="Availability: Immediate Joiner | Open to Relocation Across India & Remote", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(sec_gap)

    def header(title):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 10.2 * scale)
        pdf.set_text_color(20, 50, 90)
        pdf.cell(w=pdf.epw, h=5.5 * scale, text=clean(title.upper()), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(20, 50, 90)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1.8 * scale)

    if data.get("summary"):
        header("Professional Summary")
        pdf.set_font("Helvetica", "", body_font)
        write_block(data["summary"])
        pdf.ln(sec_gap)

    if data.get("skills"):
        header("Technical & Compliance Core Skills")
        pdf.set_font("Helvetica", "", body_font)
        for s in data["skills"]:
            write_block(s)
        pdf.ln(sec_gap)

    if data.get("experience"):
        header("Professional Experience & Security Engineering")
        for exp in data["experience"]:
            pdf.set_font("Helvetica", "B", 9.8 * scale)
            write_block(exp.get("title", ""), h=5.0 * scale)
            pdf.set_font("Helvetica", "", body_font)
            for b in exp.get("bullets", []):
                write_block(f"  - {b}")
            pdf.ln(1.8 * scale)

    if data.get("education"):
        header("Education, Certifications & Academic Projects")
        pdf.set_font("Helvetica", "", body_font)
        for item in data["education"]:
            write_block(f"  - {item}")

    return pdf

def save_pdf(data, filepath):
    # Try scales from spacious (1.14) down to compact (0.85) to fill ~93% of 1 page
    chosen_pdf = None
    for s in [1.14, 1.10, 1.06, 1.02, 0.98, 0.94, 0.90, 0.86]:
        candidate = render_with_scale(data, s)
        if candidate.get_y() <= 283:
            chosen_pdf = candidate
            break
    if chosen_pdf is None:
        chosen_pdf = render_with_scale(data, 0.84)
    chosen_pdf.output(filepath)

def analyze_fast(prompt):
    for model_name in MODELS:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            return json.loads(res.text)
        except Exception:
            time.sleep(0.5)
    return None

print(f"Fast-scanning top {len(jobs)} jobs (ATS >= {MIN_SCORE}%)...\n")

for idx, row in jobs.iterrows():
    title = str(row.get("title", "Role"))
    company = str(row.get("company", "Company"))
    url = str(row.get("job_url", ""))
    jd = str(row.get("description", ""))
    loc = str(row.get("location", "India"))
    region = str(row.get("target_region", "India"))

    if not jd or jd == "nan":
        continue

    print(f"[{idx + 1}/{len(jobs)}] {title} at {company}...", end=" ", flush=True)
    prompt = f"""
    Compare this Resume against the Job Description. Never invent fake experience or tools.
    Preserve ALL experience roles, projects, certifications, and detailed technical bullets from the original resume while tailoring keywords to match the JD.
    Return ONLY valid JSON:
    {{
      "ats_score": 85,
      "cover_note": "3-sentence human recruiter message explaining fit",
      "tailored_resume": {{
        "name": "GABY SAJI",
        "contact": "Kerala, India | (+91) 9447518866 | gabysajithomas@outlook.com",
        "summary": "3-4 sentence tailored summary",
        "skills": ["Category: detailed skill list"],
        "experience": [{{"title": "Company | Role | Dates", "bullets": ["Detailed bullet with metrics and tools"]}}],
        "education": ["Degree / Certification / Dissertation line"]
      }}
    }}
    --- RESUME ---
    {base_resume}
    --- JOB DESCRIPTION ---
    {jd[:3500]}
    """

    result = analyze_fast(prompt)
    if not result:
        print("Skipped (API busy)")
        continue

    score = result.get("ats_score", 0)
    visa_ok = result.get("visa_viable", True)
    visa_note = result.get("sponsorship_note", "N/A")
    sal_note = result.get("salary_note", "Not listed")

    if score < MIN_SCORE or not visa_ok:
        with open(seen_file, "a") as sf:
            sf.write(url + "\n")
        reason = "No Sponsorship/Local Only" if not visa_ok else "Below Threshold"
        print(f"{score}% ({reason} - Skipped)")
        continue

    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", f"{company}_{title}")[:40]
    folder = os.path.join("applications", safe_name)
    os.makedirs(folder, exist_ok=True)

    pdf_path = os.path.join(folder, f"Resume_{safe_name}.pdf")
    save_pdf(result["tailored_resume"], pdf_path)

    with open(os.path.join(folder, "cover_note.txt"), "w") as cf:
        cf.write(result.get("cover_note", ""))

    tracker_rows.append({
        "ATS_Score": score,
        "Region": region,
        "Location": loc,
        "Company": company,
        "Role": title,
        "Sponsorship": visa_note,
        "Salary_Info": sal_note,
        "Resume_PDF": pdf_path,
        "Apply_URL": url,
        "Status": "Ready to Submit"
    })
    with open(seen_file, "a") as sf:
        sf.write(url + "\n")
    print(f"{score}% -> Saved!")

if tracker_rows:
    new_df = pd.DataFrame(tracker_rows)
    if os.path.exists("tracker.csv"):
        old_df = pd.read_csv("tracker.csv")
        df_out = pd.concat([old_df, new_df], ignore_index=True).drop_duplicates(subset=["Apply_URL"])
    else:
        df_out = new_df
    df_out = df_out.sort_values(by="ATS_Score", ascending=False)
    df_out.to_csv("tracker.csv", index=False)
    open(seen_file, "w").writelines(open(seen_file).readlines()[-500:])
    print(f"\nDone in seconds! Saved {len(df_out)} balanced 1-page packets to tracker.csv.")
