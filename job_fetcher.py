import time
import pandas as pd
from jobspy import scrape_jobs

# Majority India (~75%) + Fast-Settlement UAE hubs (~25%)
queries = [
    ("Cyber Security Engineer", "India", "India", 8),
    ("SOC Analyst", "Bengaluru, Karnataka, India", "India", 6),
    ("Detection Engineer", "India", "India", 5),
    ("Cloud Security Engineer", "Kochi, Kerala, India", "India", 5),
    ("Cyber Security Engineer", "Dubai, United Arab Emirates", "United Arab Emirates", 4),
    ("SOC Analyst", "Abu Dhabi, United Arab Emirates", "United Arab Emirates", 4),
]

all_jobs = []
for term, loc, country, count in queries:
    print(f"Searching ({country}): {term} in {loc}...")
    try:
        df = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location=loc,
            results_wanted=count,
            hours_old=72,
            country_indeed=country,
            linkedin_fetch_description=False,
        )
        if df is not None and not df.empty:
            df["target_region"] = country
            all_jobs.append(df)
    except Exception as e:
        print(f"  (Skipped {term} in {loc}: {e})")
    time.sleep(3)

jobs = pd.concat(all_jobs, ignore_index=True).drop_duplicates(subset=["job_url"])
jobs = jobs[~jobs["title"].str.contains("Director|Principal|VP|Head of", case=False, na=False)]

print(f"\nFound {len(jobs)} unique jobs across India & UAE!\n")
jobs.to_csv("jobs.csv", index=False)
print("Saved all job details to jobs.csv!")
