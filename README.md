# Push API
The simple push notification API built for developers.

## Local setup

### env setup
`python -m venv env`
`source env/bin/activate`
`pip install -r requirements.txt`

### docker setup
`docker-compose up -d` 

## db management

Reset: drop all tables, run migrations and seed
`python -m app.db.manage reset`

Seed: run seed
`python -m app.db.manage seed`

Migrate: run new migrations
`python -m app.db.manage migrate`

## Running

Development (Hot reload)
`python main.py`

Production
`gunicorn main:app`

## Railway setup

1. Connect this root folder from github
2. Add a postgres db
3. set env vars for DATABASE_URL using the instance
4. set up deploy commands:
- Pre deploy `python -m app.db.manage reset`
- Deploy `gunicorn main:app`