import os
from datetime import timedelta

class TestingConfig:
    # Basic Flask configuration
    SECRET_KEY = 'test-secret-key'
    DEBUG = False
    TESTING = True

    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/uploads')
    ALLOWED_EXTENSIONS = {'csv'}

    # Geocoding configuration
    GEOCODING_API_KEY = 'test-api-key'
    GEOCODING_CACHE_TTL = timedelta(minutes=5)
    GEOCODING_RATE_LIMIT = 1000  # requests per day

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cache configuration
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 60

    # Report generation configuration
    REPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/reports')
    REPORT_TEMPLATES = {
        'summary': 'templates/reports/summary.html',
        'detailed': 'templates/reports/detailed.html'
    }

    # Map configuration
    MAP_CENTER = [40.7128, -74.0060]  # Default to NYC
    MAP_ZOOM = 12
    MAP_TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
    MAP_TILE_ATTRIBUTION = '© OpenStreetMap contributors'

    # Analysis configuration
    DEFAULT_THRESHOLD = 500
    DIRECTION_ANGLES = {
        'north': (315, 45),
        'east': (45, 135),
        'south': (135, 225),
        'west': (225, 315)
    } 