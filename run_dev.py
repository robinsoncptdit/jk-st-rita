import os
import sys
from dotenv import load_dotenv

def run_development_server():
    """Run the Flask development server with hot reloading."""
    # Load environment variables
    load_dotenv()
    
    # Set Flask environment variables
    os.environ['FLASK_APP'] = 'app'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    # Import Flask app
    from app import create_app
    app = create_app()
    
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )

if __name__ == '__main__':
    run_development_server() 