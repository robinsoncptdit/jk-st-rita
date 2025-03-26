import pytest
from unittest.mock import patch

def test_analysis_page(client):
    """Test that the analysis page loads correctly."""
    response = client.get('/analysis')
    assert response.status_code == 200
    assert b'Analysis Configuration' in response.data
    assert b'Reference Point' in response.data

def test_geocoding_endpoint(client):
    """Test the geocoding endpoint."""
    test_address = "123 Main St, New York, NY 10001"
    response = client.post('/api/geocode', json={'addresses': [test_address]})
    
    assert response.status_code == 200
    assert 'successful' in response.json
    assert len(response.json['successful']) > 0
    assert 'lat' in response.json['successful'][0]
    assert 'lng' in response.json['successful'][0]

def test_geocoding_invalid_address(client):
    """Test geocoding with an invalid address."""
    response = client.post('/api/geocode', json={'addresses': ['invalid address']})
    
    assert response.status_code == 200
    assert 'successful' in response.json
    assert 'failed' in response.json
    assert len(response.json['successful']) == 0
    assert len(response.json['failed']) == 1

def test_analysis_endpoint(client, mock_geocoding_response):
    """Test the analysis endpoint with mock data."""
    test_data = {
        'reference_point': {
            'address': '123 Main St, New York, NY 10001',
            'lat': 40.7128,
            'lng': -74.0060
        },
        'directions': ['north', 'south', 'east', 'west'],
        'threshold': 500
    }
    
    with patch('app.services.geocoding.GeocodingService.geocode_addresses') as mock_geocode:
        mock_geocode.return_value = mock_geocoding_response
        
        response = client.post('/api/analyze', json=test_data)
        
        assert response.status_code == 200
        assert 'stats' in response.json
        assert 'points' in response.json
        assert 'reference_point' in response.json

def test_analysis_invalid_reference(client):
    """Test analysis with invalid reference point."""
    test_data = {
        'reference_point': {
            'address': 'invalid address',
            'lat': 0,
            'lng': 0
        },
        'directions': ['north'],
        'threshold': 500
    }
    
    response = client.post('/api/analyze', json=test_data)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid reference point' in response.json['error']

def test_analysis_invalid_directions(client):
    """Test analysis with invalid directions."""
    test_data = {
        'reference_point': {
            'address': '123 Main St, New York, NY 10001',
            'lat': 40.7128,
            'lng': -74.0060
        },
        'directions': ['invalid'],
        'threshold': 500
    }
    
    response = client.post('/api/analyze', json=test_data)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid directions' in response.json['error']

def test_analysis_invalid_threshold(client):
    """Test analysis with invalid threshold."""
    test_data = {
        'reference_point': {
            'address': '123 Main St, New York, NY 10001',
            'lat': 40.7128,
            'lng': -74.0060
        },
        'directions': ['north'],
        'threshold': -100
    }
    
    response = client.post('/api/analyze', json=test_data)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid threshold' in response.json['error'] 