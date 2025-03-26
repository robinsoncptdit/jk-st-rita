import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def init_db():
    """Initialize the database."""
    print("Initializing database...")
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.create_all()
    print("Database initialized successfully")

def migrate_db():
    """Run database migrations."""
    print("Running database migrations...")
    subprocess.run(['flask', 'db', 'upgrade'])
    print("Database migrations completed")

def rollback_db():
    """Rollback the last database migration."""
    print("Rolling back last migration...")
    subprocess.run(['flask', 'db', 'downgrade'])
    print("Migration rolled back successfully")

def reset_db():
    """Reset the database by dropping all tables and recreating them."""
    print("Resetting database...")
    from app import create_app, db
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
    print("Database reset successfully")

def show_migrations():
    """Show the current migration status."""
    print("Current migration status:")
    subprocess.run(['flask', 'db', 'current'])
    print("\nMigration history:")
    subprocess.run(['flask', 'db', 'history'])

def main():
    """Database management CLI."""
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python manage_db.py [command]")
        print("\nAvailable commands:")
        print("  init     - Initialize the database")
        print("  migrate  - Run database migrations")
        print("  rollback - Rollback the last migration")
        print("  reset    - Reset the database")
        print("  status   - Show migration status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'migrate':
        migrate_db()
    elif command == 'rollback':
        rollback_db()
    elif command == 'reset':
        reset_db()
    elif command == 'status':
        show_migrations()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main() 