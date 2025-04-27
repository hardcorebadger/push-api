# Push API
The simple push notification API built for developers.

## Local setup

### env setup
`python -m venv env`
`source env/bin/activate`
`pip install -m requirements.txt`

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