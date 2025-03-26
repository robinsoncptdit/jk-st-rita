# Housing & Income Analysis Tool: Deployment Guide

## Deployment Overview

This document outlines the deployment process and infrastructure requirements for the Housing & Income Analysis Tool. The application is designed to be deployable in multiple environments, from local development to production.

## Deployment Options

### 1. Local Development Deployment

#### Prerequisites
- Python 3.9+ installed
- pip package manager
- Git (for version control)

#### Setup Steps
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/housing-analysis-app.git
   cd housing-analysis-app
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables
   ```bash
   # Create a .env file
   touch .env
   # Add necessary variables to .env
   echo "FLASK_APP=run.py" >> .env
   echo "FLASK_ENV=development" >> .env
   echo "SECRET_KEY=your_development_secret_key" >> .env
   echo "GEOCODING_API_KEY=your_api_key" >> .env
   ```

5. Run the application
   ```bash
   flask run
   ```

### 2. Docker Deployment

#### Prerequisites
- Docker installed
- Docker Compose (optional, for multi-container setup)

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
```

#### Docker Compose (Optional)
For setups requiring Redis for caching or other services:

```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_APP=run.py
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - GEOCODING_API_KEY=${GEOCODING_API_KEY}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

#### Deployment Steps
1. Build the Docker image
   ```bash
   docker build -t housing-analysis-app .
   ```

2. Run the container
   ```bash
   docker run -p 5000:5000 -e SECRET_KEY=your_secret -e GEOCODING_API_KEY=your_key housing-analysis-app
   ```

   Or with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### 3. Cloud Deployment

#### Option A: Heroku Deployment

1. Prerequisites
   - Heroku CLI installed
   - Heroku account

2. Create Procfile
   ```
   web: gunicorn run:app
   ```

3. Deployment Steps
   ```bash
   # Login to Heroku
   heroku login
   
   # Create a new Heroku app
   heroku create housing-analysis-app
   
   # Add Redis add-on (optional)
   heroku addons:create heroku-redis:hobby-dev
   
   # Set environment variables
   heroku config:set SECRET_KEY=your_production_secret_key
   heroku config:set GEOCODING_API_KEY=your_api_key
   
   # Deploy application
   git push heroku main
   
   # Open the application
   heroku open
   ```

#### Option B: AWS Deployment

1. Prerequisites
   - AWS account
   - AWS CLI configured
   - Elastic Beanstalk CLI (optional)

2. Create `requirements.txt` (if not already present)
   ```
   Flask==2.0.1
   pandas==1.3.0
   folium==0.12.1
   gunicorn==20.1.0
   geopy==2.2.0
   Flask-WTF==0.15.1
   reportlab==3.5.68
   python-dotenv==0.19.0
   ```

3. Deployment with Elastic Beanstalk
   ```bash
   # Initialize Elastic Beanstalk application
   eb init -p python-3.8 housing-analysis-app
   
   # Create an environment
   eb create housing-analysis-production
   
   # Set environment variables
   eb setenv SECRET_KEY=your_production_secret_key GEOCODING_API_KEY=your_api_key
   
   # Deploy application
   eb deploy
   
   # Open application in browser
   eb open
   ```

## Environment Variables

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `FLASK_APP` | Defines the Flask application entry point | `run.py` |
| `FLASK_ENV` | Sets the environment (development/production) | `production` |
| `SECRET_KEY` | Secret key for session security | `supersecretkey123` |
| `GEOCODING_API_KEY` | API key for geocoding service | `your_google_maps_api_key` |
| `CACHE_TYPE` | Type of cache to use | `redis` or `simple` |
| `REDIS_URL` | URL for Redis (if used) | `redis://localhost:6379/0` |
| `DEBUG` | Enable debug mode | `False` in production |
| `LOG_LEVEL` | Logging level | `INFO` or `ERROR` |

## Infrastructure Requirements

### Minimum Requirements
- CPU: 1 vCPU
- RAM: 1GB
- Storage: 10GB
- Network: Public internet access for geocoding API calls

### Recommended Requirements
- CPU: 2+ vCPUs
- RAM: 4GB+
- Storage: 20GB+ SSD
- Network: Public internet access with decent bandwidth

### Scaling Considerations
- Memory usage increases with dataset size
- Consider adding more RAM for processing large CSV files
- CPU utilization increases during geocoding and analysis operations

## Security Configuration

### SSL/TLS Setup
```bash
# Using Let's Encrypt with Certbot
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Or for manual HTTPS configuration with Nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Database Setup (Optional)

For persistent storage of geocoding results or user accounts:

### SQLite (Simple Setup)
```python
# config.py
SQLALCHEMY_DATABASE_URI = 'sqlite:///housing_analysis.db'
```

### PostgreSQL (Production)
```bash
# Create database
createdb housing_analysis

# Environment variable
export DATABASE_URL="postgresql://username:password@localhost/housing_analysis"
```

## Backup and Recovery

### Backup Strategy
1. Application code: Git repository
2. Database (if used): Regular dumps
   ```bash
   # PostgreSQL backup
   pg_dump housing_analysis > backup_$(date +%Y%m%d).sql
   ```
3. Environment variables: Securely stored `.env` backups
4. User-uploaded data: Regular copy to backup storage

### Recovery Procedure
1. Redeploy application from Git
2. Restore database from backup
   ```bash
   # PostgreSQL restore
   psql housing_analysis < backup_20230101.sql
   ```
3. Restore environment configuration
4. Verify application functionality

## Monitoring and Logging

### Logging Configuration
```python
# logging_config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Tools
- Application health: Heartbeat endpoint (`/health`)
- Performance monitoring: Prometheus + Grafana
- Error tracking: Sentry

## Performance Tuning

### Application Server
```ini
# gunicorn.conf.py
workers = 4  # Number of worker processes
worker_class = 'gevent'  # Async worker type
keepalive = 5  # Connection keepalive
timeout = 120  # Worker timeout for long-running operations
```

### Caching Configuration
```python
# For Redis caching
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour
```

## Upgrading Process

### Standard Upgrade Procedure
1. Announce maintenance window (if applicable)
2. Create backup of current state
3. Pull latest changes from repository
4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
5. Apply database migrations (if applicable)
6. Restart application
   ```bash
   sudo systemctl restart housing-analysis
   ```
7. Verify functionality
8. Update monitoring thresholds if needed

### Rollback Procedure
1. Stop the current version
2. Restore code from previous release tag
3. Restore database if needed
4. Restart with previous configuration
5. Verify functionality
6. Notify users of rollback

## Troubleshooting

### Common Issues

#### Application Won't Start
- Check environment variables are correctly set
- Verify Python version compatibility
- Check dependencies are installed correctly

#### Geocoding Failures
- Verify API key is valid
- Check API usage limits
- Ensure network connectivity to geocoding service

#### Performance Issues
- Check memory usage during CSV processing
- Monitor CPU during analysis operations
- Consider upgrading server resources

#### Database Connectivity (if applicable)
- Verify connection strings
- Check database server is running
- Review firewall rules

### Support Resources
- GitHub Issues: https://github.com/yourusername/housing-analysis-app/issues
- Documentation: https://housing-analysis-app.readthedocs.io/
- Email Support: support@example.com 