import os
import pytest
from flask import Flask
from app import create_app
from app.models import db
from config.testing import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestingConfig)
    
    # Create test directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Clean up after tests
    with app.app_context():
        db.session.remove()
        db.drop_all()
    
    # Remove test files
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file))
    for file in os.listdir(app.config['REPORT_FOLDER']):
        os.remove(os.path.join(app.config['REPORT_FOLDER'], file))

@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """Create a test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def sample_csv_data():
    """Create sample CSV data for testing."""
    return """address,contribution_amount
123 Main St, New York, NY 10001,500
456 Park Ave, New York, NY 10002,750
789 Broadway, New York, NY 10003,1000"""

@pytest.fixture(scope='function')
def sample_csv_file(app, sample_csv_data):
    """Create a temporary CSV file for testing."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_data.csv')
    with open(file_path, 'w') as f:
        f.write(sample_csv_data)
    return file_path

@pytest.fixture(scope='function')
def mock_geocoding_response():
    """Create mock geocoding response for testing."""
    return {
        'successful': [
            {
                'address': '123 Main St, New York, NY 10001',
                'lat': 40.7128,
                'lng': -74.0060
            },
            {
                'address': '456 Park Ave, New York, NY 10002',
                'lat': 40.7580,
                'lng': -73.9855
            },
            {
                'address': '789 Broadway, New York, NY 10003',
                'lat': 40.7196,
                'lng': -74.0027
            }
        ],
        'failed': []
    } 