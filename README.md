# VGAC Web Services

Current tagging and database access tools for annotated images for VGAC

Link to Live Site: https://vgac.cs.pomona.edu/

Link to Staging Site: https://vgac.cs.pomona.edu/staging/

Link to Paper: [EXAG 2019](http://www.exag.org/papers/EXAG_2019_paper_13.pdf)

## Table of Contents

- [Local Development](#Local\ Development)
- [vgac.cs.pomona](#VGAC.CS.POMONA)
- [Services](#services)

## LOCAL DEVELOPMENT

### Download and Setup for local development
```
git clone $URL $FOLDER
cd $FOLDER
```
You should change the `server` variable in /nginx_config/default.conf from `vgac.cs.pomona.edu` to `localhost` for local development (though this may not be a breaking change for nginx / your browser).

### Just adding webpages
If you don't need the whole server running on your computer and just want to add/edit files in the `static` directory, you can use a site like https://jsfiddle.net/ or https://codepen.io/ to sketch out html, css, and js without the hastle of a browser. It may even help fetching data from the live server.

### Launch Docker network
The next step requires docker to be [installed](https://docs.docker.com/v17.09/engine/installation/#supported-platforms), you probably want the stable Community Edition.

If you update any of the docker images you'll need to rebuild them, it is often easiest to just re-run this command.
```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

(You can use the `-d` flag to get back control of your terminal window after launching, but then it's easier to forget to shut down the docker containers in the background)

This strategy also allows 'hot-reloading' your static folder, as it is volume bound to the nginx reverse-proxy in docker-compose.dev.yml. So if you edit an html file `/static/html/test_changes.html` (or .js) and then reload the page https://localhost/html/test_changes.html in your browser you should see your changes. (You should also look into disabling caching for your browser so that it always sends the full request to your development server. In Chrome and Firefox `ctrl-shift-i` should get you to developer tools and there should be some settings to not cache while in dev mode). 

This spins up fresh instances of the nginx reverse-proxy, database, dbapi, expert api, and single-tile api containers if they don't already exist.

It fetches db connection and local file information from .env file.

Requires db_manager to run if database is not filled already (See DB Manager section below)

Some example data is provided in `text/testdata` to be ingested by the DB Manager. For getting different game data you should set up a different folder for that, `/testfolder/games` is a good choice for a name, as testfolder is .gitignored'd by default so you won't upload a bunch of data by accident. (Current vgac zip available at vgac tagging project). 

After docker-compose up runs you should be able to navigate to https://localhost/html/expert.html (or just localhost) and be served a page. Use the DB Manager to add data

### Launch DB Manager

For interactively updating and bouncing database. Docker python image with one manager script. Expects .env file or command line --env variables with database connection variables, also expects volume mounts as source / dest on host filesystem when run.
The following POSTGRES variables are taken from an env file or defaulted to the second value
```
keys = {'host': os.getenv('POSTGRES_HOST', 'vgac-db'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'dbname': os.getenv('POSTGRES_DB', 'affordances_db'),
            'user': os.getenv('POSTGRES_USER', 'faim_lab'),
            'password': os.getenv('POSTGRES_PASSWORD', 'dev'),
    }
```

The following mount locations (-v) will work if you have a dataset folder in your current directory (path result of `pwd`), otherwise use absolute path to folder
```
docker run -it --network=vgac-network -v "$(pwd)/test/testdata":/app/games:z db-manager
```

### Using DB Manager
The docker run command gives you a python interpreter with a 'manage' object created

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

To Confirm data export is equivalent, ingest filesystem data then export to filesystem and run `diff -rq /path../in_dataset /path../out_dataset` if it returns blank there are no differing files

for updating db_manager, it should be rebuilt (unless in image store CI). Gets rebuilt by docker-compose currently
```
docker build -t db-manager -f Dockerfile-db-manager ./db_manager
```


## VGAC.CS.POMONA
### Adding game data to Server
```
scp -r -i ~/.ssh/PRIVATE_KEY ./webservices_dataset username@vgac.cs.pomona.edu:/webservices
```

### Adding game data to Database
The following command is relevant to server on vgac.cs.pomona.edu updating production database (change postgres_host to vgac-db-staging for staging)
```
docker run -it --network=vgac-network -v "/webservices/webservices_dataset":/app/games:z -v "/webservices/out_dataset":/app/out_dataset:z -e POSTGRES_HOST=vgac-db gerardrbentley/vgac-webservices:db-manager-production
```

## Database
```
docker exec -it vgac-db psql -U faim_lab -d affordances_db
```

Postgres Database can be spun up in its own docker container. For persistent storage, volume is mounted to host system. For easier connection to other docker containers and not revealing ports to world it is named and on the network. Otherwise started with base docker-compose.

```
docker run -d --name vgac-db -e POSTGRES_USER postgres -e POSTGRES_DB postgres --network=vgac-network -v ./tmp_postgres=/var/lib/postgresql/data
```

[Reference][https://hub.docker.com/_/postgres]

## Services

### Adding A Service
Tagging services hosted are rerouted from /tagging/$SERVICE to /static/html/$SERVICE.html
Service API's are registered with their own base, example /expert/get_image
Not all services need to be spun up to access one, but a given service will not work correctly without adding its docker container

Adding a clause like the following to default.conf will redirect to the service if available, but not fail if it isn't present
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
