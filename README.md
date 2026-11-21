# Auto-Apply Assistant

A personal tool I am building from scratch on my MacBook Air M2 to match my resume against job descriptions, optimize for ATS, and streamline job applications.

## Build Log
- **Day 1:** Set up the project workspace, Python virtual environment, and Git repository.
- **Milestone 1 (Completed):** Built `ats_matcher.py` using Python and the Gemini API (`gemini-3.5-flash-lite`). Hit a quick snag where older model names timed out or returned 404, queried the API directly to check available models, and got my first working ATS Match Score (65%) + honest bullet rewrites.
- **Milestone 2 (Completed):** Built `resume_tailor.py` using `fpdf2` and Gemini structured JSON output to generate clean, ATS-friendly PDFs. Solved two formatting bugs along the way: handling empty lines in `fpdf2` and resetting cursor margins (`new_x="LMARGIN"`) so bullet points don't drift sideways.
- **Milestone 3 (Completed):** Built `job_fetcher.py` using `python-jobspy` to pull live job postings and full descriptions from Indeed and LinkedIn into `jobs.csv` without needing a heavy browser running in the background.
