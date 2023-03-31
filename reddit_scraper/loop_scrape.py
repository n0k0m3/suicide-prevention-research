import subprocess
import os
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SUBREDDIT = "SuicideWatch"
for year in range(2017, 2023)[::-1]:
    for month in range(1, 13)[::-1]:
        start = time.time()
        subprocess.run(["bash", "archive_scrape.sh", f"{year}-{month:02d}", SUBREDDIT])
        end = time.time()
        print(f"Finished scraping {year}-{month:02d} in {end-start:.2f} seconds")
