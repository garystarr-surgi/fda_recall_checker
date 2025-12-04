"""
Setup script for FDA Recall Checker
Initializes the database and optionally fetches initial data
"""
import sys
from app import app, init_db

def setup():
    """Initialize the application"""
    print("Initializing FDA Recall Checker...")
    
    # Initialize database
    print("Creating database tables...")
    init_db()
    print("✓ Database initialized")
    
    # Ask if user wants to fetch initial data
    if len(sys.argv) > 1 and sys.argv[1] == '--fetch':
        print("\nFetching initial data from FDA API...")
        from fetch_fda_recalls import fetch_fda_recalls
        result = fetch_fda_recalls()
        print(f"✓ {result}")
    
    print("\nSetup complete!")
    print("\nTo start the development server, run:")
    print("  python3 run.py")
    print("\nOr to start in production mode:")
    print("  gunicorn -c gunicorn_config.py wsgi:app")

if __name__ == '__main__':
    setup()

