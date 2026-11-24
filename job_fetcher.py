import os
import time
import pandas as pd
from jobspy import scrape_jobs

# Tier 1: Fast-Settlement Priority (India, UAE, Germany) + Tier 2: Open Worldwide / Remote
queries = [
    # Priority 1: India (Core Base)
    ("Cyber Security Engineer", "India", "India", 10),
    ("SOC Analyst", "India", "India", 8),
    ("Detection Engineer", "India", "India", 6),
    ("Cloud Security Engineer", "India", "India", 6),
    ("Information Security Analyst", "India", "India", 6),
    # Priority 2: UAE & Germany (Fastest International Settlement)
    ("Cyber Security Engineer", "United Arab Emirates", "United Arab Emirates", 8),
    ("SOC Analyst", "United Arab Emirates", "United Arab Emirates", 6),
    ("Cyber Security Engineer", "Germany", "Germany", 8),
    ("SOC Analyst", "Germany", "Germany", 6),
    # Tier 3: Open Worldwide / Remote (Unlocked Global Opportunities)
    ("Cyber Security Engineer", "Remote", "Worldwide", 8),
    ("SOC Analyst", "Remote", "Worldwide", 6),
    ("Cloud Security Engineer", "Remote", "Worldwide", 6),
    # Tier 4: Global Tech & Lifestyle Hubs (Europe, APAC, Middle East, Americas)
    ("Cyber Security Engineer", "Netherlands", "Netherlands", 5),
    ("Cyber Security Engineer", "Switzerland", "Switzerland", 5),
    ("Cyber Security Engineer", "UK", "UK", 5),
    ("Cyber Security Engineer", "Ireland", "Ireland", 4),
    ("Cyber Security Engineer", "Austria", "Austria", 4),
    ("Cyber Security Engineer", "Singapore", "Singapore", 5),
    ("Cyber Security Engineer", "Canada", "Canada", 5),
    ("Cyber Security Engineer", "Australia", "Australia", 5),
    ("Cyber Security Engineer", "Saudi Arabia", "Saudi Arabia", 4),
    ("Cyber Security Engineer", "Qatar", "Qatar", 4),
]

SITE_LIMITS = {"linkedin": 4, "glassdoor": 4, "zip_recruiter": 4, "naukri": 4}
site_counts = {k: 0 for k in SITE_LIMITS}
blocked_sites = set()

seen_urls = set()
if os.path.exists("seen_jobs.txt"):
    seen_urls = set(l.strip() for l in open("seen_jobs.txt") if l.strip())

all_jobs = []

def run_board(site, term, loc, region_label, count, delay=1.5):
    if site in blocked_sites:
        return
    if site in SITE_LIMITS and site_counts[site] >= SITE_LIMITS[site]:
        return
    try:
        kwargs = {
            "site_name": [site],
            "search_term": term,
            "location": loc,
            "results_wanted": count,
            "hours_old": 168,
            "country_indeed": "India" if region_label == "Worldwide" else region_label,
        }
        if site == "linkedin":
            kwargs["linkedin_fetch_description"] = False
            if region_label == "Worldwide":
                kwargs["is_remote"] = True
        df = scrape_jobs(**kwargs)
        if site in SITE_LIMITS:
            site_counts[site] += 1
        if df is not None and not df.empty:
            df["target_region"] = region_label
            all_jobs.append(df)
            print(f"  [{site}] +{len(df)} roles")
    except Exception as e:
        err = str(e)
        if "429" in err or "block" in err.lower():
            blocked_sites.add(site)
            print(f"  [{site}] Rate-limited (429) — pausing {site} for remainder of run.")
        else:
            print(f"  [{site}] Skipped ({region_label}): {err[:60]}")
    time.sleep(delay)

for term, loc, region_label, count in queries:
    print(f"Searching ({region_label}): {term}...")
    run_board("indeed", term, loc, region_label, count, delay=1.2)
    if region_label == "India":
        run_board("naukri", term, loc, region_label, 5, delay=2.0)
    if region_label in ("Worldwide", "United Arab Emirates", "Germany", "India"):
        run_board("linkedin", term, loc, region_label, 4, delay=5.0)
    if region_label in ("Worldwide", "UK", "Germany", "Netherlands", "Canada", "Australia", "India"):
        run_board("glassdoor", term, loc, region_label, 4, delay=2.5)
    if region_label in ("Worldwide", "UK", "Canada"):
        run_board("zip_recruiter", term, loc, region_label, 4, delay=2.0)

if all_jobs:
    jobs = pd.concat(all_jobs, ignore_index=True).drop_duplicates(subset=["job_url"])
    jobs = jobs[~jobs["title"].str.contains("Director|Principal|VP|Head of", case=False, na=False)]
    new_jobs = jobs[~jobs["job_url"].isin(seen_urls)]
    print(f"\nFound {len(jobs)} total roles worldwide, {len(new_jobs)} brand-new unseen roles!")
    new_jobs.to_csv("jobs.csv", index=False)
else:
    print("\nNo jobs returned this run.")
