
# Setup

## Start DB
`cd infra && docker-compose up -d`

## Create Tables
`python3 scripts/set_database_tables.py`

## Ingest Data
`python3 scripts/ingest.py`
Comment out data loaders you don't want. For example if you don't have a gmail token, comment out the gmail loader.
Fill the file_folder with the files you want to index.

## Run app
Create a project in xcode to run swift app
When you run the app, it'll ask what folder it should have permission to read from. Choose any folder that contains this repo.

## Run Server
`uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload`
