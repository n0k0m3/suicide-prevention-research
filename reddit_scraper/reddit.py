import praw
from pmaw import PushshiftAPI
import json
import datetime as dt
import sqlite3
from time import sleep
import pymongo


class RedditScrape:
    def __init__(
        self,
        subreddit: str,
        db_con: pymongo.database.Database,
        praw_enriched: praw.reddit.Reddit = None,
        min_total: int = 1000,
        retry_limit: int = 10,
        collection_name: str = None,
    ):
        self.subreddit = subreddit

        self.db = db_con
        self.collection = self.db[self.subreddit]

        self.api = PushshiftAPI(praw=praw_enriched)

        self.before = int(dt.datetime.now().timestamp())

        self.min_total = min_total
        self.retry_limit = retry_limit

    def check_before(self):
        if self.collection.count_documents({}) == 0:
            before = int(dt.datetime.now().timestamp())
        else:
            before = self.collection.find_one(sort=[("created_utc", 1)])["created_utc"]
        return int(before) - 1

    def scrape(self, method: str = "pmaw", collection_name: str = None):
        if collection_name:
            self.collection = self.db[collection_name]

        self.before = self.check_before()
        if method == "pmaw":
            self.scrape_pmaw()
        elif method in ["praw", "reddit"]:
            self.scrape_reddit()

    def scrape_reddit(self):
        # should we implement this? Reddit API is very limited
        pass

    def scrape_pmaw(self):
        while self.collection.count_documents({}) < self.min_total:
            posts = self.api.search_submissions(
                subreddit=self.subreddit, limit=1000, until=self.before
            )
            new_post_list = list(posts)

            # retry until getting response from pushshift API or out of retries
            if len(new_post_list) == 0:
                if self.retry_limit == 0:
                    print(
                        f"Failed to get more responses from pushshift API for /r/{self.subreddit}"
                    )
                    print("Ending scrape")
                    return None
                sleep(10)
                self.retry_limit -= 1
                continue

            # update self.before for next query
            self.before = int(new_post_list[-1]["created_utc"] - 1)

            # filter out removed posts and posts with no text
            post_list = [
                post
                for post in new_post_list
                if post["removed_by_category"] is None and len(post["selftext"]) > 3
            ]  # slow step

            # process responses for insertion into db
            for post in new_post_list:
                post.pop("_reddit")
                post["subreddit"] = self.subreddit
                if post["author"] is not None:
                    post["author"] = post["author"].name

            print(f"Inserting {len(post_list)} posts from /r/{self.subreddit}")
            self.collection.insert_many(post_list)

        return None


def scrape_subreddit(
    subreddit: str,
    db_con: sqlite3.Connection,
    min_total: int = 1000,
    retry_limit: int = 10,
):
    api = PushshiftAPI(praw=reddit)
    cur = db_con.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {subreddit} (selftext TEXT)")
    post_list = []
    before = int(dt.datetime.now().timestamp())
    while len(post_list) < min_total:
        posts = api.search_submissions(subreddit=subreddit, limit=1000, until=before)
        new_post_list = list(posts)
        if len(new_post_list) == 0:
            if retry_limit == 0:
                print(
                    f"Failed to get more responses from pushshift API for /r/{subreddit}"
                )
                return None
            sleep(10)
            retry_limit -= 1
            # retry until getting response from pushshift API
            continue
        before = int(new_post_list[-1]["created_utc"] - 1)
        post_list = [
            post
            for post in new_post_list
            if post["removed_by_category"] is None and len(post["selftext"]) > 3
        ]  # slow step
        print(f"Inserting {len(post_list)} posts from /r/{subreddit}")
        cur.executemany(f"INSERT INTO {subreddit} VALUES(?)", post_list)

    db_con.commit()
    return None


def scrape_subreddit_praw():
    for submission in reddit.subreddit("SuicideWatch").new(limit=10):
        sub = submission.__dict__
        sub.pop("_reddit")
        sub["subreddit"] = sub["subreddit"].display_name
        sub["author"] = sub["author"].name
        print(json.dumps(sub, indent=4))
        break


if __name__ == "__main__":
    with open("secrets.json", "r") as f:
        secrets = json.loads(f.read())["REDDIT_SECRETS"]

    reddit = praw.Reddit(
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        user_agent=f"python: PMAW request enrichment",
    )

    from database import get_db_conn_string

    myclient = pymongo.MongoClient(get_db_conn_string())
    db = myclient["IRI"]
    reddit_suicide = RedditScrape("SuicideWatch", db, reddit, min_total=10000)
    reddit_suicide.scrape_pmaw()
    # Pushshift API limited to post after 1667504602
    # Get Pushshift dump prior: https://files.pushshift.io/reddit/submissions/
