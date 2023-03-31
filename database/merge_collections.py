import pymongo

COMMON_KEYS = [
    "author_flair_css_class",
    "link_flair_css_class",
    "edited",
    "url",
    "permalink",
    "author",
    "selftext",
    "subreddit_id",
    "media_embed",
    "author_flair_text",
    "is_self",
    "gilded",
    "title",
    "locked",
    "subreddit",
    "contest_mode",
    "_id",
    "over_18",
    "spoiler",
    "score",
    "num_comments",
    "domain",
    "id",
    "distinguished",
    "suggested_sort",
    "hidden",
    "media",
    "archived",
    "link_flair_text",
    "secure_media",
    "secure_media_embed",
    "thumbnail",
    "created_utc",
    "stickied",
]

REMOVED = ["[removed]", "[deleted]"]

if __name__ == "__main__":
    from database import get_db_conn_string

    client = pymongo.MongoClient(get_db_conn_string())
    db_staging = client["IRI_staging"]
    db_main = client["IRI"]
    collection_main = db_main["SuicideWatch"]

    for collection_name in db_staging.list_collection_names():
        if collection_name == "system.indexes":
            continue
        collection_staging = db_staging[collection_name]
        # print(collection_name)
        # copy all documents from staging to main using aggregation
        project_keys = {key: 1 for key in COMMON_KEYS}
        project_keys["_id"] = 0
        author_filter = {"author": {"$nin": REMOVED}}
        selftext_filter = {"selftext": {"$nin": REMOVED}}
        # add selftext filter for post with length > 0
        selftext_filter["$or"] = [
            {"selftext": {"$exists": False}},
            {"selftext": {"$gt": ""}},
        ]
        # add author filter eliminate null authors
        author_filter["$or"] = [{"author": {"$exists": False}}, {"author": {"$gt": ""}}]
        filter = {"$and": [author_filter, selftext_filter]}
        # pipeline to filter out removed/deleted posts
        pipeline = [
            {"$match": filter},
            {"$project": project_keys},
            {"$merge": {"into": {"db": "IRI", "coll": "SuicideWatch"}}},
        ]
        collection_staging.aggregate(pipeline)
