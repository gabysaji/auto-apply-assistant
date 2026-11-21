import pandas as pd
from jobspy import scrape_jobs

queries = [
    ("Cyber Security Engineer", "India"),
    ("SOC Analyst", "Bengaluru, Karnataka, India"),
    ("Detection Engineer", "India"),
    ("Cloud Security Engineer", "Kochi, Kerala, India"),
]

all_jobs = []
for term, loc in queries:
    print(f"Searching: {term} in {loc}...")
    df = scrape_jobs(
        site_name=["indeed", "linkedin"],
        search_term=term,
        location=loc,
        results_wanted=5,
        hours_old=48,
        country_indeed="India",
        linkedin_fetch_description=True,
    )
    all_jobs.append(df)

jobs = pd.concat(all_jobs, ignore_index=True).drop_duplicates(subset=["job_url"])
print(f"\nFound {len(jobs)} unique cybersecurity jobs!\n")
for idx, row in jobs.iterrows():
    print(f"{idx + 1}. {row.get('title')} at {row.get('company')} ({row.get('location')})")
    print(f"   Link: {row.get('job_url')}\n")

jobs.to_csv("jobs.csv", index=False)
print("Saved all job details to jobs.csv!")
