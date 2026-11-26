import os, re, time, json
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fpdf import FPDF

load_dotenv()
client = genai.Client(http_options={"timeout": 15000})

LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://www.linkedin.com")
GITHUB_URL = os.getenv("GITHUB_URL", "https://github.com")
MODELS = ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-3.8-flash"]
MIN_SCORE = 70
MAX_JOBS = 25

if not os.path.exists("my_resume.txt") or not open("my_resume.txt").read().strip():
    print("ERROR: my_resume.txt is empty! Please upload or paste your resume in the Profile & API Settings tab first.")
    raise SystemExit(1)
base_resume = open("my_resume.txt").read()
extra_exp = open("extra_experience.txt").read().strip() if os.path.exists("extra_experience.txt") else ""
seen_file = "seen_jobs.txt"
seen_urls = set(l.strip() for l in open(seen_file) if l.strip()) if os.path.exists(seen_file) else set()

raw_jobs = pd.read_csv("jobs.csv")
jobs = raw_jobs[~raw_jobs["job_url"].isin(seen_urls)].head(MAX_JOBS)
os.makedirs("applications", exist_ok=True)
tracker_rows = []

def clean(text):
    t = str(text)
    for ch in ["\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "\u2212"]:
        t = t.replace(ch, "-")
    for ch in ["\u2018", "\u2019", "\u201c", "\u201d"]:
        t = t.replace(ch, "'")
    t = re.sub(r"[^\x20-\x7E\n]", "-", t)
    return re.sub(r"-{2,}", "-", t).strip()

def render_with_scale(data, scale):
    pdf = FPDF()
    pdf.set_margins(12, 12 * scale, 12)
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)
    bf, lh, sg = 9.5 * scale, 4.6 * scale, 2.8 * scale

    def wb(text, h=lh):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(w=pdf.epw, h=h, text=clean(text), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 17 * scale)
    pdf.cell(w=pdf.epw, h=7.5 * scale, text=clean(data.get("name", "YOUR FULL NAME")), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9.2 * scale)
    pdf.set_text_color(60, 60, 60)
    cb_items = [x.strip() for x in clean(data.get("contact", "")).split("|") if x.strip() and "linkedin" not in x.lower() and "github" not in x.lower()]
    tokens = [(x, f"mailto:{x}" if "@" in x else "") for x in cb_items] + [("LinkedIn", LINKEDIN_URL), ("GitHub", GITHUB_URL)]
    sep = " | "
    total_w = sum(pdf.get_string_width(t) for t, _ in tokens) + pdf.get_string_width(sep) * (len(tokens) - 1)
    pdf.set_x((pdf.w - total_w) / 2)
    for idx, (t, lnk) in enumerate(tokens):
        if idx > 0:
            pdf.set_text_color(60, 60, 60); pdf.set_font("Helvetica", "", 9.2 * scale)
            pdf.cell(w=pdf.get_string_width(sep), h=5 * scale, text=sep)
        if lnk:
            pdf.set_text_color(15, 80, 160); pdf.set_font("Helvetica", "U", 9.2 * scale)
            pdf.cell(w=pdf.get_string_width(t), h=5 * scale, text=t, link=lnk)
        else:
            pdf.set_text_color(60, 60, 60); pdf.set_font("Helvetica", "", 9.2 * scale)
            pdf.cell(w=pdf.get_string_width(t), h=5 * scale, text=t)
    pdf.ln(5 * scale)

    pdf.set_text_color(40, 40, 40); pdf.set_font("Helvetica", "I", 8.8 * scale)
    reg = str(data.get("region", "India")).strip()
    avail = "Availability: Immediate Joiner | Open to Relocation Across India & Remote" if reg.lower() in ("india", "", "nan") else f"Availability: Immediate Joiner | Open to Immediate Relocation to {reg}"
    pdf.cell(w=pdf.epw, h=4.8 * scale, text=avail, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0); pdf.ln(sg)

    def hdr(t):
        pdf.set_x(pdf.l_margin); pdf.set_font("Helvetica", "B", 10.2 * scale); pdf.set_text_color(20, 50, 90)
        pdf.cell(w=pdf.epw, h=5.5 * scale, text=clean(t.upper()), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(20, 50, 90); pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.set_text_color(0, 0, 0); pdf.ln(1.8 * scale)

        if data.get("summary"):
        hdr("Professional Summary"); pdf.set_font("Helvetica", "", bf); wb(data["summary"]); pdf.ln(sg)
    if data.get("skills"):
        hdr("Technical & Compliance Core Skills"); pdf.set_font("Helvetica", "", bf)
        sk = data.get("skills", "")
        wb(" | ".join(sk) if isinstance(sk, list) else " | ".join([x.strip(" -•") for x in re.split(r"[\n|]+", str(sk)) if x.strip()]), h=4.8 * scale)
        pdf.ln(sg)
    if data.get("experience"):
        hdr("Professional Experience & Security Engineering")
        for exp in data["experience"]:
        pdf.set_x(pdf.l_margin)
        role_t = clean(exp.get("role", ""))
            comp_t = clean(exp.get("company", ""))
            loc_t = clean(exp.get("location", ""))
            right_d = clean(exp.get("dates", ""))

            if not role_t and exp.get("title"):
                parts = [x.strip() for x in clean(exp.get("title", "")).split("|") if x.strip()]
                role_t = parts.pop(0) if parts else ""
                if parts and any(m in parts[-1] for m in ["202", "201", "Present", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]):
                    right_d = parts.pop(-1)
                comp_t = parts.pop(0) if parts else ""
                loc_t = " - ".join(parts)

            if "experion" in role_t.lower() and comp_t:
                role_t, comp_t = comp_t, role_t

            sub_left = f"{comp_t} - {loc_t}" if (comp_t and loc_t and comp_t.lower() != loc_t.lower()) else (comp_t or loc_t)

            if role_t:
                pdf.set_font("Helvetica", "B", 9.8 * scale)
                wb(role_t, h=4.8 * scale)
            if sub_left or right_d:
                pdf.set_x(pdf.l_margin)
                pdf.set_font("Helvetica", "I", 9.2 * scale)
                dw = (pdf.get_string_width(right_d) + 3) if right_d else 0
                if sub_left and right_d and (pdf.get_string_width(sub_left) + dw <= pdf.epw):
                    pdf.cell(w=pdf.epw - dw, h=4.6 * scale, text=sub_left)
                    pdf.cell(w=dw, h=4.6 * scale, text=right_d, align="R", new_x="LMARGIN", new_y="NEXT")
                elif sub_left:
                    wb(f"{sub_left} | {right_d}" if right_d else sub_left, h=4.6 * scale)
                else:
                    pdf.cell(w=pdf.epw, h=4.6 * scale, text=right_d, align="R", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", bf)
            for b in exp.get("bullets", []): wb(f"  - {b}")
            pdf.ln(1.8 * scale)
    if data.get("education"):
        hdr("Education, Certifications & Academic Projects"); pdf.set_font("Helvetica", "", bf)
        for item in data["education"]: wb(f"  - {item}")
    return pdf

def save_pdf(data, filepath):
    for s in [1.14, 1.10, 1.06, 1.02, 0.98, 0.94, 0.90, 0.86, 0.84]:
        cand = render_with_scale(data, s)
        if cand.get_y() <= 283 or s == 0.84:
            cand.output(filepath)
            break

def save_cover_letter_pdf(letter_text, region, filepath):
    pdf = FPDF()
    pdf.set_margins(16, 16, 16)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(w=pdf.epw, h=7.5, text="YOUR FULL NAME", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9.2)
    pdf.set_text_color(60, 60, 60)
    cb = "City, Country | Phone | Email"
    bw, lw, sw, gw = pdf.get_string_width(cb + " | "), pdf.get_string_width("LinkedIn"), pdf.get_string_width(" | "), pdf.get_string_width("GitHub")
    pdf.set_x((pdf.w - (bw + lw + sw + gw)) / 2)
    pdf.cell(w=bw, h=5, text=cb + " | ")
    pdf.set_text_color(15, 80, 160); pdf.set_font("Helvetica", "U", 9.2)
    pdf.cell(w=lw, h=5, text="LinkedIn", link=LINKEDIN_URL)
    pdf.set_text_color(60, 60, 60); pdf.set_font("Helvetica", "", 9.2)
    pdf.cell(w=sw, h=5, text=" | ")
    pdf.set_text_color(15, 80, 160); pdf.set_font("Helvetica", "U", 9.2)
    pdf.cell(w=gw, h=5, text="GitHub", link=GITHUB_URL, new_x="LMARGIN", new_y="NEXT")

    pdf.set_text_color(40, 40, 40); pdf.set_font("Helvetica", "I", 8.8)
    reg = str(region).strip()
    avail = "Availability: Immediate Joiner | Open to Relocation Across India & Remote" if reg.lower() in ("india", "", "nan") else f"Availability: Immediate Joiner | Open to Immediate Relocation to {reg}"
    pdf.cell(w=pdf.epw, h=4.8, text=avail, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_draw_color(20, 50, 90)
    pdf.ln(2)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.set_text_color(0, 0, 0)
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 10.5)
    for para in str(letter_text).split("\n"):
        line = clean(para)
        if line:
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=pdf.epw, h=5.5, text=line, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

    pdf.output(filepath)

def analyze_fast(prompt):
    for m in MODELS:
        try:
            res = client.models.generate_content(model=m, contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json"))
            return json.loads(res.text)
        except Exception:
            time.sleep(0.5)
    return None

print(f"Fast-scanning {len(jobs)} new jobs (ATS >= {MIN_SCORE}%)...\n")

for idx, row in jobs.iterrows():
    title, company = str(row.get("title", "Role")), str(row.get("company", "Company"))
    url, jd = str(row.get("job_url", "")), str(row.get("description", ""))
    loc, region = str(row.get("location", "India")), str(row.get("target_region", "India"))
    if not jd or jd == "nan": continue

    print(f"[{idx + 1}] {title} at {company} ({region})...", end=" ", flush=True)
    prompt = f"""Compare Resume vs JD for an Indian candidate (UK MSc Cyber Security, immediate joiner). Target: {region} ({loc}).
Never invent fake experience/tools. ALWAYS preserve exact job title, company name, workplace location (e.g. Trivandrum, Kerala), and exact start/end dates from the resume.
DYNAMIC EXPERIENCE-STAGE RULE (Adapts to ANY candidate's resume):
1. First calculate the candidate's actual years of full-time experience (Y) from their resume (counting internships/academic work as ~0-1 yr Entry-Level).
2. PRIORITY MATCH (85-98%): Roles matching the candidate's actual career stage (e.g., if Y <= 2, prioritize Entry-Level, Graduate, Associate & 0-3 yr roles; if Y = 10, prioritize Senior, Staff, Principal & 7-12 yr roles).
3. STRETCH MATCH (72-82%): Roles up to 2-4 years above or slightly below their level when technical skills align strongly, so they still appear in the queue ranked just below priority matches.
4. MISMATCH CAP (55%): Cap ats_score at 55 ONLY if the role is grossly mismatched to the candidate's resume (e.g., requiring 5+ years MORE than the candidate actually has, or an entry-level internship for a 10-year veteran).
Keep ALL roles by default (visa_viable=true), including silent sponsorship. Set visa_viable=false ONLY if JD explicitly says "no sponsorship", "citizens/nationals only", or mandatory C1 local language.
VOICE RULE: "linkedin_note", "recruiter_email", and "cover_letter" MUST be written in FIRST PERSON ("I", "my", "me") as the candidate—NEVER third person.
"linkedin_note" MUST be strictly under 275 characters for a free LinkedIn connection note.
"recruiter_details": Extract ONLY real recruiter/hiring contact info explicitly written in the JD (Name, Email, Phone number, or LinkedIn URL). If NO contact info or name is mentioned in the JD, return strictly "NONE".
Return ONLY JSON:
{{"ats_score": 85, "visa_viable": true, "sponsorship_note": "...", "salary_note": "Avg: [Realistic market range in local currency] | Quote: [Recommended ask for UK MSc + 1yr SOC exp]", "recruiter_details": "...", "linkedin_note": "...", "recruiter_email": "Subject: ...\n\n...", "cover_letter": "...", "tailored_resume": {{"name": "YOUR FULL NAME", "contact": "City, Country | Phone | Email", "summary": "...", "skills": ["..."], "experience": [{{"role": "Exact Job Title", "company": "Company Name", "location": "City, State/Country (e.g. Trivandrum, Kerala)", "dates": "Exact Dates from Resume (e.g. Feb 2026 - Sep 2026)", "bullets": ["..."]}}], "education": ["..."]}}}}
OPTIONAL EXTRA EXPERIENCE/PROJECTS BANK (Include ONLY if directly relevant to this specific JD; omit if unrelated):\n{extra_exp[:2000]}\n--- RESUME ---\n{base_resume}\n--- JD ---\n{jd[:3500]}"""

    result = analyze_fast(prompt)
    if not result:
        print("Skipped (API busy)"); continue

    score, visa_ok = result.get("ats_score", 0), result.get("visa_viable", True)
    if score < MIN_SCORE or not visa_ok:
        open(seen_file, "a").write(url + "\n")
        print(f"{score}% (Skipped)"); continue

    cand_clean = re.sub(r"[^a-zA-Z0-9]+", "_", clean(result["tailored_resume"].get("name", "Candidate"))).strip("_")
    role_clean = re.sub(r"[^a-zA-Z0-9]+", "_", title).strip("_")[:30]
    folder_slug = re.sub(r"[^a-zA-Z0-9]+", "_", f"{company}_{title}").strip("_")[:40]
    folder = os.path.join("applications", folder_slug)
    os.makedirs(folder, exist_ok=True)
    pdf_path = os.path.join(folder, f"{cand_clean}_{role_clean}_Resume.pdf")
    result["tailored_resume"]["region"] = region
    save_pdf(result["tailored_resume"], pdf_path)

    li_note = result.get("linkedin_note", "").strip()
    if len(li_note) > 280:
        li_note = li_note[:277].rsplit(" ", 1)[0] + "..."

    open(os.path.join(folder, "linkedin_note.txt"), "w").write(li_note)
    open(os.path.join(folder, "recruiter_email.txt"), "w").write(result.get("recruiter_email", "").strip())
    cl_text = result.get("cover_letter", "").strip()
    open(os.path.join(folder, "cover_letter.txt"), "w").write(cl_text)
    cl_pdf_path = os.path.join(folder, f"{cand_clean}_{role_clean}_Cover_Letter.pdf")
    save_cover_letter_pdf(cl_text, region, cl_pdf_path)
    open(os.path.join(folder, "recruiter_info.txt"), "w").write(result.get("recruiter_details", "").strip())

    tracker_rows.append({"ATS_Score": score, "Region": region, "Location": loc, "Company": company, "Role": title, "Sponsorship": result.get("sponsorship_note", "N/A"), "Salary_Info": result.get("salary_note", "Not listed"), "Resume_PDF": pdf_path, "Apply_URL": url, "Status": "Ready to Submit"})
    open(seen_file, "a").write(url + "\n")
    print(f"{score}% -> Saved!")

if tracker_rows:
    new_df = pd.DataFrame(tracker_rows)
    df_out = pd.concat([pd.read_csv("tracker.csv"), new_df], ignore_index=True).drop_duplicates(subset=["Apply_URL"]) if os.path.exists("tracker.csv") else new_df
    df_out.sort_values(by="ATS_Score", ascending=False).to_csv("tracker.csv", index=False)
    open(seen_file, "w").writelines(open(seen_file).readlines()[-500:])
    print(f"\nDone! Saved {len(new_df)} complete first-person application packets.")
else:
    print("\nDone! No new roles met the threshold.")
