# Auto-Apply Assistant

An open-source, human-in-the-loop AI job application pipeline and Streamlit dashboard powered by **Python**, **JobSpy**, and the **Google Gemini API**. Built to automate global job discovery, ATS fit scoring, country-adaptive 1-page resume & cover letter PDF generation, and personalized first-person outreach—while keeping your API keys, resume, and personal data 100% private on your machine.

## Key Features

- **1-Click Global & Regional Job Discovery:** Aggregates openings from Indeed, Naukri, Glassdoor, ZipRecruiter, and capped LinkedIn queries with built-in `429` rate-limit circuit breakers and deduplication (`seen_jobs.txt`).
- **Dynamic Experience-Stage ATS Scoring:** Automatically evaluates your actual experience level from your resume (from internships/graduates to 10+ year veterans), prioritizing roles that match your career stage while surfacing stretch opportunities.
- **Country-Aware Resume Standards:** Automatically adapts PDF paper size (**US Letter** for North America vs. **A4** for UK, EU/DACH, UAE/GCC, and India), spelling conventions (US vs. UK English), and regional compliance/relocation framing.
- **Tailor Custom JD (Offline & Manual Roles):** Paste any offline, recruiter-emailed, or private portal job description to generate a tailored 1-page Resume PDF, Cover Letter PDF, LinkedIn note, and recruiter email on demand.
- **Zero-Code Profile & Experience Bank:** Drag-and-drop an existing `.pdf`, `.docx`, or `.txt` resume in the UI, and store extra projects/experience in a private conditional bank (`extra_experience.txt`) that is woven into tailored CVs *only* when relevant to the target job.
- **ATS-Standard Naming & Clickable Links:** Exports clean single-page PDFs named `FirstName_LastName_Role_Resume.pdf` and `FirstName_LastName_Role_Cover_Letter.pdf` with flush-right employment dates and clickable `mailto:`, LinkedIn, and GitHub header links.
- **Privacy-First Architecture:** All personal files (`.env`, `my_resume.txt`, `extra_experience.txt`, `tracker.csv`, `jobs.csv`, `seen_jobs.txt`, and `applications/`) are excluded via `.gitignore`.

## Quick Start

### 1. Clone & Install
```bash
git clone https://://github.com
cd auto-apply-assistant
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Launch the Dashboard
```bash
streamlit run app.py
```

### 3. Configure & Run
1. Open the **Profile & API Settings** tab in your browser.
2. Enter your free Gemini API key (from `https://://google.com`), add your LinkedIn/GitHub URLs, and upload your `.pdf`, `.docx`, or `.txt` resume.
3. Click **Find & Tailor New Jobs** in the sidebar (or paste any offline job description in the **Tailor Custom JD** tab) to generate ready-to-submit application packets.

## Updating Your Local Copy
If you cloned this repository earlier and want the latest features:
```bash
git pull && pip install -r requirements.txt
```
