# VGAC Web Services

Current tagging and database access tools for annotated images for VGAC

Link to Paper: [EXAG 2019](http://www.exag.org/papers/EXAG_2019_paper_13.pdf)

## Table of Contents

- [Setup](#setup)
- [Services](#services)

## Setup

### LOCAL DEVELOPMENT

```
git clone $URL $FOLDER
cd $FOLDER
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

This spins up fresh instances of the db, dbapi, and nginx containers if they don't already exist. Also currently starts a db_manager and expert container.
Fetches db connection information from .env file.
Requires db_manager to run if database is not filled already

You should copy the contents of /nginx_config/ into /dev_config/ and set a localhost server in main_nginx.conf
By default the db-manager will use /testfolder/games and /testfolder/out_data for ingesting and bouncing, so you should populate games (current vgac zip available at vgac tagging project). 
(testfolder and dev_config are .gitignored'd by default, so you have to add them to your local set up)
See docker-compose.dev.yml for host mounted location info


After docker-compose up runs you should be able to navigate to http://localhost/html/expert.html and be served a page. Use the DB Manager to add data

### DB Manager

For interactively updating and bouncing database. Docker python image with one manager script. Expects .env file with database connection variables, also expects volume mounts as source / dest on host filesystem when run.
The following POSTGRES variables are taken from an env file or defaulted to the second value
```
keys = {'host': os.getenv('POSTGRES_HOST', 'vgac-db'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'dbname': os.getenv('POSTGRES_DB', 'affordances_db'),
            'user': os.getenv('POSTGRES_USER', 'faim_lab'),
            'password': os.getenv('POSTGRES_PASSWORD', 'dev'),
    }
```

```
docker run -it --env-file .env --network=vgac-network -v "/USER/PATH/THIS_FOLDER/testfolder/games":/app/games:z -v "/USER/PATH/THIS_FOLDER/testfolder/out_data":/app/out_dataset:z db-manager
```
(replacing /USER/PATH/THIS_FOLDER with something like /Users/username/vgac_web or whatever `pwd` tells you)

This launches python interpreter with a 'manage' object created

The Main commands for this manage object are:
```
# removes all tables and data from db (DANGER)
manage.drop_all()
# initializes 6 tables for vgac db
manage.init_tables()
# ingests data from the folder mounted to '/app/games' in docker container
manage.ingest_filesystem_data()
# exports data to the folder mounted to '/app/out_dataset' in docker container
manage.export_to_filesystem()

# ingests screenshot and tag data for a given game and folder
manage.ingest_screenshots('gamename', '/app/games/gamename/screenshots')
# ingests tile and tag data for a given game and folder
manage.ingest_tiles('gamename', '/app/games/gamename/tiles')
```

for updating db_manager, it should be rebuilt (unless in image store CI). Gets rebuilt by docker-compose currently
```
docker build -t db-manager -f Dockerfile-db-manager ./db_manager
```

## CS1
### Adding game data
```
scp -r -i ~/.ssh/PRIVATE_KEY ./games faim@pom-itb-cs1.campus.pomona.edu:/data/faim
```

## Services

### Adding A Service
Tagging services hosted are rerouted from /tagging/$SERVICE to /static/html/$SERVICE.html
Service API's are registered with their own base, example /expert/get_image
Not all services need to be spun up to access one, but a given service will not work correctly without adding its docker container

Adding a clause like the following to main_nginx.conf will redirect to the service if available, but not fail if it isn't present
```
location ~ ^/myService/(.*)$ {
        resolver 127.0.0.11 valid=30s;
        set $upstream http://myService:5000;
        proxy_pass $upstream/$1$is_args$args;
    }
```

Build any new services then be sure to run with the --network=vgac-network flag to connect to the DB API
```
docker build -t tagging-service-name -f Dockerfile-tagging-service ./tagging-service-folder
docker run --network=vgac-network tagging-service-name
```
For more on docker run see [[https://docs.docker.com/engine/reference/run/][run]] and post on [[https://stackify.com/docker-build-a-beginners-guide-to-building-docker-images/][build]] 


### Database
```
docker exec -it vgac-db psql -U faim_lab -d affordances_db
```

Postgres Database can be spun up in its own docker container. For persistent storage, volume is mounted to host system. For easier connection to other docker containers and not revealing ports to world it is named and on the network. Otherwise started with base docker-compose.

```
docker run -d --name vgac-db -e POSTGRES_USER postgres -e POSTGRES_DB postgres --network=vgac-network -v ./tmp_postgres=/var/lib/postgresql/data
```

[Reference][https://hub.docker.com/_/postgres]