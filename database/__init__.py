import pymongo
import json
import os


def get_db_conn_string():
    connection_string = os.getenv("MONGO_CONNECTION_STRING")
    if connection_string is not None:
        return connection_string
    elif os.path.exists("secrets.json"):
        with open("secrets.json", "r") as f:
            db = json.loads(f.read())["DB_SECRETS"]
        return f"mongodb://{db['DB_USER']}:{db['DB_PASS']}@{db['DB_HOST']}:{db['DB_PORT']}/"
    else:
        print("No connection string or db.json found\n")
        print("Please set the MONGO_CONNECTION_STRING environment variable")
        print(
            'Example:\nexport MONGO_CONNECTION_STRING="mongodb://root:example@localhost:27017/"\n'
        )
        print("Or create a db.json file with the following format:")
        print(
            json.dumps(
                {
                    "DB_HOST": "localhost",
                    "DB_PORT": "27017",
                    "DB_USER": "root",
                    "DB_PASS": "example",
                },
                indent=4,
            )
        )


if __name__ == "__main__":
    db_str = get_db_conn_string()
    if db_str is None:
        exit(1)
    client = pymongo.MongoClient(
        db_str, serverSelectionTimeoutMS=10, connectTimeoutMS=20000
    )
    try:
        info = client.server_info()  # Forces a call.
        print("Server is up.")
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Server is down.")
