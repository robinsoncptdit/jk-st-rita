import os
import pytest
from unittest.mock import patch

def test_reports_page(client):
    """Test that the reports page loads correctly."""
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'Reports' in response.data
    assert b'Generate New Report' in response.data

def test_generate_report_endpoint(client):
    """Test the report generation endpoint."""
    test_data = {
        'type': 'summary',
        'include_sections': ['map', 'statistics', 'data_table'],
        'threshold': 500,
        'include_directions': True
    }
    
    with patch('app.services.reporting.ReportingService.generate_report') as mock_generate:
        mock_generate.return_value = {
            'success': True,
            'report_url': '/static/reports/summary_20240320.pdf'
        }
        
        response = client.post('/api/reports/generate', json=test_data)
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'report_url' in response.json

def test_generate_report_invalid_type(client):
    """Test report generation with invalid report type."""
    test_data = {
        'type': 'invalid',
        'include_sections': ['map'],
        'threshold': 500
    }
    
    response = client.post('/api/reports/generate', json=test_data)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid report type' in response.json['error']

def test_generate_report_invalid_sections(client):
    """Test report generation with invalid sections."""
    test_data = {
        'type': 'summary',
        'include_sections': ['invalid'],
        'threshold': 500
    }
    
    response = client.post('/api/reports/generate', json=test_data)
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid sections' in response.json['error']

def test_download_report(client):
    """Test downloading a report."""
    test_report_id = 'test-report-123'
    
    with patch('app.services.reporting.ReportingService.get_report') as mock_get_report:
        mock_get_report.return_value = {
            'file_path': os.path.join('tests/reports', 'test_report.pdf'),
            'content_type': 'application/pdf'
        }
        
        response = client.get(f'/api/reports/download/{test_report_id}')
        
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'

def test_download_nonexistent_report(client):
    """Test downloading a nonexistent report."""
    test_report_id = 'nonexistent-report'
    
    with patch('app.services.reporting.ReportingService.get_report') as mock_get_report:
        mock_get_report.return_value = None
        
        response = client.get(f'/api/reports/download/{test_report_id}')
        
        assert response.status_code == 404
        assert 'error' in response.json
        assert 'Report not found' in response.json['error']

def test_delete_report(client):
    """Test deleting a report."""
    test_report_id = 'test-report-123'
    
    with patch('app.services.reporting.ReportingService.delete_report') as mock_delete:
        mock_delete.return_value = True
        
        response = client.delete(f'/api/reports/{test_report_id}')
        
        assert response.status_code == 200
        assert response.json['success'] is True

def test_delete_nonexistent_report(client):
    """Test deleting a nonexistent report."""
    test_report_id = 'nonexistent-report'
    
    with patch('app.services.reporting.ReportingService.delete_report') as mock_delete:
        mock_delete.return_value = False
        
        response = client.delete(f'/api/reports/{test_report_id}')
        
        assert response.status_code == 404
        assert 'error' in response.json
        assert 'Report not found' in response.json['error']

def test_list_reports(client):
    """Test listing available reports."""
    with patch('app.services.reporting.ReportingService.list_reports') as mock_list:
        mock_list.return_value = [
            {
                'id': 'report-1',
                'type': 'summary',
                'created_at': '2024-03-20T14:30:00',
                'file_size': 1024
            }
        ]
        
        response = client.get('/api/reports')
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0
        assert 'id' in response.json[0]
        assert 'type' in response.json[0] 