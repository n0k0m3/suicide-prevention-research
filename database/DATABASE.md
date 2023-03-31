# MongoDB Database

The scraper use MongoDB as database. To deploy a local MongoDB instance, first we create .env file from .env.example file and edit:

```sh
cp .env.example .env
#nano .env
```

Then we can start the database deployment with docker-compose:

```sh
docker-compose -f docker-compose.yml up -d
```