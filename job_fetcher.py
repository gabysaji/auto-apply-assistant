import os
import time
import pandas as pd
from jobspy import scrape_jobs

# Worldwide High-Demand & High-Lifestyle Hubs + India Majority
queries = [
    # India (Core Base)
    ("Cyber Security Engineer", "India", "India", 10),
    ("SOC Analyst", "India", "India", 8),
    ("Detection Engineer", "India", "India", 6),
    ("Cloud Security Engineer", "India", "India", 6),
    # Fast-Settlement & High-Lifestyle Middle East & Asia
    ("Cyber Security Engineer", "United Arab Emirates", "United Arab Emirates", 8),
    ("SOC Analyst", "United Arab Emirates", "United Arab Emirates", 6),
    ("Cyber Security Engineer", "Singapore", "Singapore", 6),
    # Europe (High Lifestyle & English-Friendly Tech Hubs)
    ("Cyber Security Engineer", "Germany", "Germany", 7),
    ("SOC Analyst", "Germany", "Germany", 5),
    ("Cyber Security Engineer", "Netherlands", "Netherlands", 6),
    ("Cyber Security Engineer", "Switzerland", "Switzerland", 5),
    ("Cyber Security Engineer", "UK", "UK", 6),
    ("Cyber Security Engineer", "Ireland", "Ireland", 5),
    ("Cyber Security Engineer", "Austria", "Austria", 5),
    ("Cyber Security Engineer", "Sweden", "Sweden", 5),
    ("Cyber Security Engineer", "Luxembourg", "Luxembourg", 4),
    # North America & Oceania
    ("Cyber Security Engineer", "Canada", "Canada", 6),
    ("Cyber Security Engineer", "Australia", "Australia", 6),
]

seen_urls = set()
if os.path.exists("seen_jobs.txt"):
    seen_urls = set(l.strip() for l in open("seen_jobs.txt") if l.strip())

all_jobs = []
for term, loc, region_label, count in queries:
    print(f"Searching Worldwide ({region_label}): {term}...")
    try:
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=term,
            location=loc,
            results_wanted=count,
            hours_old=168,
            country_indeed=region_label,
        )
        if df is not None and not df.empty:
            df["target_region"] = region_label
            all_jobs.append(df)
    except Exception as e:
        print(f"  (Skipped {region_label}: {e})")
    time.sleep(1.2)

if all_jobs:
    jobs = pd.concat(all_jobs, ignore_index=True).drop_duplicates(subset=["job_url"])
    jobs = jobs[~jobs["title"].str.contains("Director|Principal|VP|Head of", case=False, na=False)]
    new_jobs = jobs[~jobs["job_url"].isin(seen_urls)]
    print(f"\nFound {len(jobs)} total global roles across 13 countries, {len(new_jobs)} brand-new unseen roles!")
    new_jobs.to_csv("jobs.csv", index=False)
else:
    print("\nNo jobs returned this run.")
