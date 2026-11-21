import time
import pandas as pd
from jobspy import scrape_jobs

# Priority 1: India (Majority) | Priority 2: UAE & Germany (Fast Settlement) | Priority 3: Scotland, England, Ireland, Austria
queries = [
    ("Cyber Security Engineer", "India", "India", 6),
    ("SOC Analyst", "Bengaluru, Karnataka, India", "India", 5),
    ("Detection Engineer", "India", "India", 5),
    ("Cyber Security Engineer", "Dubai, United Arab Emirates", "United Arab Emirates", 4),
    ("SOC Analyst", "Abu Dhabi, United Arab Emirates", "United Arab Emirates", 3),
    ("Cyber Security Engineer", "Germany", "Germany", 4),
    ("SOC Analyst", "Berlin, Germany", "Germany", 3),
    ("Cyber Security Engineer", "Edinburgh, Scotland", "UK", 2),
    ("Cyber Security Engineer", "London, England", "UK", 2),
    ("Cyber Security Engineer", "Dublin, Ireland", "Ireland", 2),
    ("Cyber Security Engineer", "Vienna, Austria", "Austria", 2),
]

# Limited LinkedIn queries (capped to avoid 429 rate limits)
linkedin_queries = [
    ("Cyber Security Engineer", "United Arab Emirates", "United Arab Emirates", 3),
    ("Cyber Security Engineer", "Germany", "Germany", 3),
]

all_jobs = []

for term, loc, region_label, count in queries:
    print(f"Searching Company Sites & Indeed ({region_label}): {term} in {loc}...")
    try:
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=term,
            google_search_term=f"{term} jobs in {loc}",
            location=loc,
            results_wanted=count,
            hours_old=72,
            country_indeed=region_label,
        )
        if df is not None and not df.empty:
            df["target_region"] = region_label
            all_jobs.append(df)
    except Exception as e:
        print(f"  (Skipped {loc}: {e})")
    time.sleep(2)

for term, loc, region_label, count in linkedin_queries:
    print(f"Searching LinkedIn (Limited - {region_label}): {term}...")
    try:
        df = scrape_jobs(
            site_name=["linkedin"],
            search_term=term,
            location=loc,
            results_wanted=count,
            hours_old=72,
            linkedin_fetch_description=False,
        )
        if df is not None and not df.empty:
            df["target_region"] = region_label
            all_jobs.append(df)
    except Exception as e:
        print(f"  (LinkedIn rate-limited, skipping: {e})")
    time.sleep(6)

jobs = pd.concat(all_jobs, ignore_index=True).drop_duplicates(subset=["job_url"])
jobs = jobs[~jobs["title"].str.contains("Director|Principal|VP|Head of", case=False, na=False)]

print(f"\nFound {len(jobs)} unique jobs from Company Career Sites, Indeed & LinkedIn across all target countries!\n")
jobs.to_csv("jobs.csv", index=False)
print("Saved all job details to jobs.csv!")
