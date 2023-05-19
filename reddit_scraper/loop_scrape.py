import subprocess
import os
import time
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def scrape_call(data_source_dir, year, month, subreddit):
    # if "|" in subreddit:
    #     subreddit_0 = subreddit.split("|")[0]
    # else:
    #     subreddit_0 = subreddit
    # if os.path.exists(f"../data/{subreddit_0}/{year}-{month:02d}.json"):
    #     print(f"Skipping {year}-{month:02d} for {subreddit}")
    #     return
    start = time.time()
    subprocess.run(["bash", "archive_scrape.sh", data_source_dir, f"{year}-{month:02d}", subreddit])
    end = time.time()
    print(f"Finished scraping {year}-{month:02d} for {subreddit} in {end-start:.2f} seconds")


try:
    DATA_SOURCE_DIR = sys.argv[1]
    SUBREDDIT = sys.argv[2]
except IndexError:
    DATA_SOURCE_DIR = input("Enter data source directory: ")
    SUBREDDIT = input("Enter subreddit name: ")
if "," in SUBREDDIT:
    SUBREDDIT = SUBREDDIT.split(",")
    SUBREDDIT = "|".join(SUBREDDIT)
for year in range(2017, 2024)[::-1]:
    for month in range(1, 13)[::-1]:
        if os.path.exists(f"{DATA_SOURCE_DIR}/RS_{year}-{month:02d}.zst"):
            scrape_call(DATA_SOURCE_DIR, year, month, SUBREDDIT)