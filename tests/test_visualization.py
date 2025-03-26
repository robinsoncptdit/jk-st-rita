import pytest
from unittest.mock import patch

def test_map_view_page(client):
    """Test that the map view page loads correctly."""
    response = client.get('/map')
    assert response.status_code == 200
    assert b'Map View' in response.data
    assert b'Filters' in response.data

def test_map_data_endpoint(client, mock_geocoding_response):
    """Test the map data endpoint."""
    test_params = {
        'threshold': 500,
        'directions': ['north', 'south', 'east', 'west'],
        'min_contribution': 0,
        'max_contribution': 1000
    }
    
    with patch('app.services.visualization.VisualizationService.get_map_data') as mock_map_data:
        mock_map_data.return_value = {
            'points': [
                {
                    'address': '123 Main St',
                    'lat': 40.7128,
                    'lng': -74.0060,
                    'contribution': 750,
                    'direction': 'north'
                }
            ],
            'stats': {
                'total_records': 1,
                'contribution_stats': {
                    'mean': 750,
                    'median': 750,
                    'min': 750,
                    'max': 750,
                    'sum': 750
                },
                'direction_filtered': {
                    'north': 1,
                    'south': 0,
                    'east': 0,
                    'west': 0
                }
            }
        }
        
        response = client.get('/api/visualization/map', query_string=test_params)
        
        assert response.status_code == 200
        assert 'points' in response.json
        assert 'stats' in response.json

def test_map_data_invalid_params(client):
    """Test map data endpoint with invalid parameters."""
    test_params = {
        'threshold': -100,
        'directions': ['invalid'],
        'min_contribution': 'abc',
        'max_contribution': 'xyz'
    }
    
    response = client.get('/api/visualization/map', query_string=test_params)
    
    assert response.status_code == 400
    assert 'error' in response.json

def test_chart_data_endpoint(client):
    """Test the chart data endpoint."""
    test_params = {
        'type': 'direction',
        'threshold': 500
    }
    
    with patch('app.services.visualization.VisualizationService.get_chart_data') as mock_chart_data:
        mock_chart_data.return_value = {
            'labels': ['North', 'South', 'East', 'West'],
            'data': [10, 5, 8, 3]
        }
        
        response = client.get('/api/visualization/chart', query_string=test_params)
        
        assert response.status_code == 200
        assert 'labels' in response.json
        assert 'data' in response.json

def test_chart_data_invalid_type(client):
    """Test chart data endpoint with invalid chart type."""
    test_params = {
        'type': 'invalid',
        'threshold': 500
    }
    
    response = client.get('/api/visualization/chart', query_string=test_params)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid chart type' in response.json['error']

def test_area_selection(client):
    """Test area selection on the map."""
    test_bounds = {
        'north': 40.8,
        'south': 40.6,
        'east': -73.9,
        'west': -74.1
    }
    
    with patch('app.services.visualization.VisualizationService.get_area_data') as mock_area_data:
        mock_area_data.return_value = {
            'points': [],
            'stats': {
                'total_records': 0,
                'contribution_stats': {
                    'mean': 0,
                    'median': 0,
                    'min': 0,
                    'max': 0,
                    'sum': 0
                },
                'direction_filtered': {
                    'north': 0,
                    'south': 0,
                    'east': 0,
                    'west': 0
                }
            }
        }
        
        response = client.post('/api/visualization/area', json=test_bounds)
        
        assert response.status_code == 200
        assert 'points' in response.json
        assert 'stats' in response.json

def test_area_selection_invalid_bounds(client):
    """Test area selection with invalid bounds."""
    test_bounds = {
        'north': 'invalid',
        'south': 40.6,
        'east': -73.9,
        'west': -74.1
    }
    
    response = client.post('/api/visualization/area', json=test_bounds)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid bounds' in response.json['error'] 