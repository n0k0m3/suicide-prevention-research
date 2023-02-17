import subprocess
import os


class PushShiftScrape:
    # A wrapper to scrape from pushshift archive
    def __init__(self, subreddit: str) -> None:
        self.subreddit = subreddit

    def scrape_month(self, year: int, month: int) -> None:
        # scrape from pushshift archive
        subprocess.run(
            ["./archive_scrape.sh", f"{year}-{month}", self.subreddit], check=True
        )

    def scrape_all(self) -> None:
        # scrape from pushshift archive
        subprocess.run(["./archive_scrape.sh", "all", self.subreddit], check=True)
