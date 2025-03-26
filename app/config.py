import os

class Config:
    # Base directory of the application
    BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Geocoding configuration
    GEOCODING_PROVIDER = 'nominatim'  # Using OpenStreetMap's Nominatim service
    GEOCODING_USER_AGENT = 'housing_analysis_tool'
    
    # Cache configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Database configuration (if needed later)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    # Use a separate upload folder for testing
    UPLOAD_FOLDER = os.path.join(Config.BASEDIR, 'tests', 'uploads')

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # In production, you should set a proper secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or None
    if SECRET_KEY is None:
        raise ValueError("No SECRET_KEY set for production configuration") 