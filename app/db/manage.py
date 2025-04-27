import click
from app.db.migrations import run_migrations, seed_database, reset_database

@click.group()
def cli():
    """Database management commands"""
    pass

@cli.command()
def migrate():
    """Run database migrations"""
    run_migrations()

@cli.command()
def seed():
    """Seed the database with initial data"""
    seed_database()

@cli.command()
def reset():
    """Reset the database and run migrations and seeds"""
    reset_database()

if __name__ == '__main__':
    cli() 