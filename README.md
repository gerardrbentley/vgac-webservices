# VGAC Web Services

Current tagging and database access tools for annotated images for VGAC

Link to Paper: [EXAG 2019](http://www.exag.org/papers/EXAG_2019_paper_13.pdf)

## Table of Contents

- [Setup](#setup)
- [Services](#services)

## Setup

### NGINX, DB, DBAPI

```
git clone $URL $FOLDER
cd $FOLDER
docker-compose up
```

This spins up fresh instances of the db, dbapi, and nginx containers if they don't already exist.
Fetches db connection information from .env file.
Requires db_manager to run if database is not filled already

See docker-compose.yaml for host mounted locations

### Database

Postgres Database can be spun up in its own docker container. For persistent storage, volume is mounted to host system. For easier connection to other docker containers and not revealing ports to world it is named and on the network. Otherwise started with base docker-compose.

```
docker run -d --name vgac-db -e POSTGRES_USER postgres -e POSTGRES_DB postgres --network=vgac-network -v ./tmp_postgres=/var/lib/postgresql/data
```

[Reference][https://hub.docker.com/_/postgres]

### DB Manager

For interactively updating and bouncing database. Docker python image with one manager script. Expects .env file with database connection variables, also expects volume mounts as source / dest on host filesystem when run.

```
docker run -it --rm --env-file .env --network=vgac-network -v "/Users/GerardB/research/vgac_dbapi/gamesfolder":/app/games:z -v "/Users/GerardB/research/vgac_dbapi/outfolder":/app/out_dataset:z db_manager
```

This launches python interpreter with a 'manage' object created

The Main commands for this manage object are:
```
# removes all tables and data from db (DANGER)
manage.drop_all()
# initializes 6 tables for vgac db
manage.init_tables()
# ingests data from the folder mounted to '/games' in docker container
manage.ingest_filesystem_data()
# exports data to the folder mounted to '/out_dataset' in docker container
manage.export_to_filesystem()

# ingests screenshot and tag data for a given game and folder
manage.ingest_screenshots('gamename', 'games/gamename/screenshots')
# ingests tile and tag data for a given game and folder
manage.ingest_tiles('gamename', 'games/gamename/tiles')
```

for updating db_manager, it should be rebuilt (unless in image store CI)
```
docker build -t db_manager -f Dockerfile-db-manager ./db_manager
```


## Services

### Adding A Service
Tagging services hosted are rerouted from /tagging/$SERVICE to /static/html/$SERVICE.html
Service API's are registered with their own base, example /expert/get_image
Not all services need to be spun up to access one, but a given service will not work correctly without adding its docker container

```
cd expert
docker-compose up
```
