from jobspy import scrape_jobs

print("Searching for live jobs...")

jobs = scrape_jobs(
    site_name=["indeed", "linkedin"],
    search_term="Data Analyst",
    location="Kerala, India",
    results_wanted=5,
    hours_old=168,
    country_indeed="India",
    linkedin_fetch_description=True,
)

print(f"Found {len(jobs)} jobs!\n")
for idx, row in jobs.iterrows():
    print(f"{idx + 1}. {row.get('title')} at {row.get('company')} ({row.get('location')})")
    print(f"   Link: {row.get('job_url')}\n")

jobs.to_csv("jobs.csv", index=False)
print("Saved all job details and descriptions to jobs.csv!")
