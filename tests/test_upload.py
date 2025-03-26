import os
import pytest
from werkzeug.datastructures import FileStorage

def test_upload_page(client):
    """Test that the upload page loads correctly."""
    response = client.get('/upload')
    assert response.status_code == 200
    assert b'Upload Data' in response.data
    assert b'Drag & Drop your CSV file here' in response.data

def test_upload_valid_csv(client, sample_csv_file):
    """Test uploading a valid CSV file."""
    with open(sample_csv_file, 'rb') as f:
        data = {
            'file': (FileStorage(f), 'test_data.csv')
        }
        response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert 'file_id' in response.json

def test_upload_invalid_file(client):
    """Test uploading an invalid file type."""
    data = {
        'file': (b'not a csv file', 'test.txt')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid file type' in response.json['error']

def test_upload_empty_file(client):
    """Test uploading an empty file."""
    data = {
        'file': (b'', 'empty.csv')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Empty file' in response.json['error']

def test_upload_missing_columns(client):
    """Test uploading a CSV file with missing required columns."""
    invalid_data = """name,value
John,100
Jane,200"""
    
    data = {
        'file': (invalid_data.encode(), 'invalid.csv')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Missing required columns' in response.json['error']

def test_upload_invalid_amounts(client):
    """Test uploading a CSV file with invalid contribution amounts."""
    invalid_data = """address,contribution_amount
123 Main St,invalid
456 Park Ave,abc"""
    
    data = {
        'file': (invalid_data.encode(), 'invalid_amounts.csv')
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'Invalid contribution amounts' in response.json['error'] 