# Auto-Apply Assistant

A lightweight, human-in-the-loop job application assistant I built from scratch in Python on my MacBook Air (M2, 8 GB RAM). Instead of blindly spamming job boards with bots—which risks account bans and sends generic resumes—this tool fetches real jobs, scores them against my resume, tailors an ATS-friendly PDF resume for each role, and organizes everything into ready-to-submit folders.

## Why I Built This
Applying to dozens of jobs manually is repetitive, and sending the same generic resume rarely passes Applicant Tracking Systems (ATS). I wanted a fast, memory-light tool that handles the heavy lifting—researching roles, spotting missing keywords, and formatting clean resumes—while keeping me in full control before hitting submit.

## How It Works
1. **`job_fetcher.py`** — Searches live job listings on LinkedIn and Indeed using `python-jobspy` and saves full job descriptions to `jobs.csv`.
2. **`ats_matcher.py`** — Compares my base resume against a job description using the Google Gemini API (`gemini-3.5-flash-lite`) to calculate an ATS match score and highlight missing keywords.
3. **`resume_tailor.py`** — Rewrites resume bullets honestly using structured JSON output and renders a clean, single-column ATS-friendly PDF via `fpdf2`.
4. **`auto_apply.py`** — Runs the full pipeline end-to-end, creating a dedicated folder per job inside `applications/` with a tailored PDF resume, a custom recruiter cover note, and a `tracker.csv` spreadsheet with direct apply links.

## My Build Log (Real Bugs & Lessons Learned)
- **Day 1 — Setup & Memory Constraints:** Set up a clean Python virtual environment and `.gitignore` so API keys and personal PDFs never leak. Chose cloud Gemini APIs and pure-Python PDF generation (`fpdf2`) so the entire app runs smoothly on an 8 GB M2 MacBook Air.
- **Milestone 1 — API Model Troubleshooting:** Hit a `404 NOT_FOUND` error with older Gemini model names. Wrote a quick one-line script to query available models on my API key and switched to `gemini-3.5-flash-lite` for fast, reliable responses.
- **Milestone 2 — Fixing PDF Layout Quirks:** My first plain-text PDF looked unformatted and threw a horizontal space error on blank lines. Upgraded the prompt to return structured JSON and fixed `fpdf2` cursor alignment (`new_x="LMARGIN"`) so sections, divider lines, and bullet points render cleanly.
- **Milestone 3 — Live Job Scraping:** Integrated `python-jobspy` to pull real job postings and descriptions without needing a heavy browser running in the background.
- **Milestone 4 — Safe Human-in-the-Loop Pipeline:** Connected all stages into `auto_apply.py` to generate per-company application packets and a CSV tracker while keeping final submission manual so accounts stay 100% safe.

## Quick Start
1. Clone the repo and create a virtual environment:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install google-genai python-dotenv fpdf2 python-jobspy
   ```
2. Add your Gemini API key to a `.env` file:
   ```bash
   echo 'GEMINI_API_KEY="your_api_key_here"' > .env
   ```
3. Paste your real resume into `my_resume.txt`, set your target role/location in `job_fetcher.py`, and run:
   ```bash
   python3 job_fetcher.py
   python3 auto_apply.py
   ```
