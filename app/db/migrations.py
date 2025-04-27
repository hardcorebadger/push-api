import os
from sqlalchemy import text
from app.database import engine
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    """Run all migrations in order"""
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    
    # Get all migration files and sort them
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    with engine.connect() as conn:
        # Create migrations table if it doesn't exist
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()
        
        # Get already applied migrations
        result = conn.execute(text("SELECT name FROM migrations"))
        applied_migrations = {row[0] for row in result}
        
        # Apply new migrations
        for migration_file in migration_files:
            if migration_file not in applied_migrations:
                print(f"Applying migration: {migration_file}")
                with open(os.path.join(migrations_dir, migration_file), 'r') as f:
                    migration_sql = f.read()
                    conn.execute(text(migration_sql))
                    conn.execute(text("INSERT INTO migrations (name) VALUES (:name)"), 
                               {"name": migration_file})
                    conn.commit()
                print(f"Applied migration: {migration_file}")

def seed_database():
    """Run seed data"""
    seed_file = os.path.join(os.path.dirname(__file__), 'seed.sql')
    
    if os.path.exists(seed_file):
        print("Seeding database...")
        with engine.connect() as conn:
            with open(seed_file, 'r') as f:
                seed_sql = f.read()
                conn.execute(text(seed_sql))
                conn.commit()
        print("Database seeded successfully")
    else:
        print("No seed file found")

def reset_database():
    """Reset the database by dropping all tables and running migrations and seeds"""
    print("Resetting database...")
    with engine.connect() as conn:
        # Drop all tables
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    
    # Run migrations and seed
    run_migrations()
    seed_database()
    print("Database reset complete") 