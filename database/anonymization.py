import pymongo
from uuid import uuid4
from bson.binary import UuidRepresentation
from database import get_db_conn_string

client = pymongo.MongoClient(get_db_conn_string(), uuidRepresentation="standard")
db = client["IRI"]
# collection = db["SuicideWatch"]

# ######################################
# ### Split Selftext and Metadata ######
# ######################################
# # split the collection into two collections, one for just self text and one for other metadata, with _id as primary key

# # get all keys in the collection
# keys = collection.find_one().keys()

# # selftext collection
# collection.aggregate(
#     [
#         {"$project": {"_id": 1, "selftext": 1}},
#         {"$out": "SuicideWatch_selftext"},
#     ]
# )

# # metadata collection
# project_keys = {key: 1 for key in keys}
# project_keys.pop("selftext")
# project_keys["_id"] = 1
# collection.aggregate([{"$project": project_keys}, {"$out": "SuicideWatch_metadata"}])

# ######################################
# ### Anonymize Author and Author_id ###
# ######################################
# # get unique authors
# authors = collection.distinct("author")
# # create unique id for each author
# author_ids = {author: uuid4() for author in authors}
# # create author_id field in metadata collection
collection_metadata = db["SuicideWatch_metadata"]
# collection_metadata.update_many({}, {"$set": {"author_id": ""}})
# i = 0
# for author, author_id in author_ids.items():
#     collection_metadata.update_many(
#         {"author": author}, {"$set": {"author_id": author_id}}
#     )
#     i += 1
#     if i % 1000 == 0:
#         print("Processed {} users".format(i))

######################################
# Split Author and Selftext metadata #
######################################
# split collection_metadata into two collections, one for just author and one for other metadata, with author_ids as primary key
# author metadata: author_id, author, author_flair_css_class, author_flair_text

# get all keys in the collection
keys = collection_metadata.find_one().keys()

# author collection
collection_metadata.aggregate(
    [
        {
            "$project": {
                "_id": 0,
                "author_id": 1,
                "author": 1,
                "author_flair_css_class": 1,
                "author_flair_text": 1,
            }
        },
        {"$out": "SuicideWatch_author_metadata"},
    ]
)

# metadata collection
project_keys = {key: 1 for key in keys}
project_keys.pop("author")
project_keys.pop("author_flair_css_class")
project_keys.pop("author_flair_text")
project_keys["_id"] = 0
collection_metadata.aggregate(
    [{"$project": project_keys}, {"$out": "SuicideWatch_post_metadata"}]
)
