import os
import sys
import pytest
from coverage import Coverage

def run_tests():
    """Run tests with coverage reporting."""
    # Create coverage object
    cov = Coverage(
        branch=True,
        source=['app'],
        omit=[
            '*/tests/*',
            '*/venv/*',
            '*/env/*',
            '*/__init__.py',
            '*/config/*'
        ]
    )
    
    # Start coverage measurement
    cov.start()
    
    # Run tests
    test_args = [
        'tests/',
        '-v',
        '--tb=short',
        '--cov=app',
        '--cov-report=term-missing',
        '--cov-report=html'
    ]
    
    if len(sys.argv) > 1:
        test_args.extend(sys.argv[1:])
    
    pytest.main(test_args)
    
    # Stop coverage measurement
    cov.stop()
    
    # Save coverage data
    cov.save()
    
    # Print coverage report
    print('\nCoverage Report:')
    cov.report()
    
    # Generate HTML report
    cov.html_report(directory='coverage_html')

if __name__ == '__main__':
    run_tests() 