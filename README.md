# Auto-Apply Assistant

A lightweight, human-in-the-loop AI job application command center built in Python and Streamlit. It fetches international roles, scores them via the Google Gemini API, generates tailored single-page resumes and cover letters, drafts outreach notes, and tracks everything in a visual dashboard.

## Key Features

- **Visual Command Center (`app.py`):** Manage active queues, filter by country, update statuses, and copy outreach drafts.
- **Multi-Country Job Search (`job_fetcher.py`):** Scans live listings across India, UAE, Germany, UK, Ireland, and Austria while preventing duplicates (`seen_jobs.txt`).
- **Smart ATS Scoring (`auto_apply.py`):** Evaluates technical alignment, visa rules, and salary benchmarks.
- **Single-Page PDFs:** Builds auto-balanced resume and cover letter PDFs with active links and relocation headers.
- **Outreach Assets:** Drafts concise LinkedIn connection notes, emails, and cover letters in first-person voice.
- **Zero-Code Onboarding:** Configure your Gemini API key, profile URLs, and resume inside the browser settings tab.

## Quick Start (Mac & Linux)

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com
   cd auto-apply-assistant
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```
3. Open the **Profile & API Settings** tab in your browser, enter your Gemini API key, links, and resume, save settings, and use the sidebar to fetch and tailor roles.

## Quick Start (Windows)

1. Clone the repository and install dependencies:
   ```powershell
   git clone https://github.com
   cd auto-apply-assistant
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Launch the dashboard:
   ```powershell
   streamlit run app.py
   ```
3. Open the **Profile & API Settings** tab in your browser to save your Gemini API key, profile links, and resume, then run the pipeline from the sidebar.

## Privacy & Safety

- Local files (`.env`, `my_resume.txt`, `tracker.csv`, `seen_jobs.txt`, `applications/`) are ignored by `.gitignore` to keep personal data safe.
- Submissions remain manual to protect job portal and LinkedIn accounts.
