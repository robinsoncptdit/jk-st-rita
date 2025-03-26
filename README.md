# Housing & Income Analysis Tool

A Flask-based web application for analyzing housing and income data with geographic visualization and reporting capabilities.

## Features

- CSV data upload and validation
- Automatic address geocoding
- Directional analysis (North, South, East, West)
- Contribution threshold filtering
- Interactive map visualization
- PDF report generation
- Comprehensive test coverage

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/housing-income-analysis.git
cd housing-income-analysis
```

2. Set up the development environment:
```bash
python setup_dev.py
```

3. Update the `.env` file with your configuration:
- Set your geocoding API key
- Adjust other settings as needed

## Development

1. Start the development server:
```bash
python run_dev.py
```

2. Run tests:
```bash
python run_tests.py
```

3. Manage the database:
```bash
# Initialize the database
python manage_db.py init

# Run migrations
python manage_db.py migrate

# Rollback last migration
python manage_db.py rollback

# Reset database
python manage_db.py reset

# Show migration status
python manage_db.py status
```

## Project Structure

```
housing-income-analysis/
├── app/
│   ├── __init__.py
│   ├── api/
│   ├── main/
│   ├── services/
│   ├── static/
│   └── templates/
├── tests/
├── uploads/
├── reports/
├── config.py
├── requirements.txt
├── setup_dev.py
├── run_dev.py
├── run_tests.py
└── manage_db.py
```

## Testing

The project uses pytest for testing. Test files are located in the `tests/` directory.

To run tests with coverage reporting:
```bash
python run_tests.py
```

Coverage reports will be generated in the `coverage_html/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 