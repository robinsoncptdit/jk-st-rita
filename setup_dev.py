import os
import subprocess
import sys
from pathlib import Path

def create_directories():
    """Create necessary directories for the application."""
    directories = [
        'app/static/css',
        'app/static/js',
        'app/static/reports',
        'app/templates/reports',
        'uploads',
        'reports',
        'tests/uploads',
        'tests/reports',
        'coverage_html'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def create_env_file():
    """Create a .env file with development settings."""
    env_content = """# Flask configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=dev-secret-key

# Geocoding configuration
GEOCODING_API_KEY=your-api-key-here

# Database configuration
DATABASE_URL=sqlite:///dev.db
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("Created .env file")

def install_dependencies():
    """Install project dependencies."""
    print("Installing dependencies...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    print("Dependencies installed successfully")

def setup_git():
    """Set up Git configuration."""
    if not os.path.exists('.git'):
        print("Initializing Git repository...")
        subprocess.run(['git', 'init'])
        subprocess.run(['git', 'add', '.'])
        subprocess.run(['git', 'commit', '-m', 'Initial commit'])
        print("Git repository initialized")
    else:
        print("Git repository already exists")

def create_gitignore():
    """Create a .gitignore file."""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Application specific
.env
*.db
uploads/*
!uploads/.gitkeep
reports/*
!reports/.gitkeep
coverage_html/

# Testing
.pytest_cache/
.coverage
htmlcov/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("Created .gitignore file")

def main():
    """Set up the development environment."""
    print("Setting up development environment...")
    
    create_directories()
    create_env_file()
    install_dependencies()
    setup_git()
    create_gitignore()
    
    print("\nDevelopment environment setup complete!")
    print("\nNext steps:")
    print("1. Update the GEOCODING_API_KEY in .env with your API key")
    print("2. Run the application: flask run")
    print("3. Run tests: python run_tests.py")

if __name__ == '__main__':
    main() 