# Housing & Income Analysis Tool: API Documentation

## API Overview

This document outlines the API endpoints and interfaces for the Housing & Income Analysis Tool. The application uses a RESTful API architecture built on Flask to handle data processing, geocoding, analysis, and reporting functions.

## API Endpoints

### 1. Data Upload API

#### `POST /api/upload`
Handles CSV file uploads and initial processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: CSV file with user data

**Response:**
```json
{
  "status": "success",
  "records_count": 150,
  "has_geocodable_addresses": true,
  "session_id": "abc123def456"
}
```

### 2. Geocoding API

#### `POST /api/geocode`
Processes addresses and converts them to coordinates.

**Request:**
```json
{
  "session_id": "abc123def456",
  "batch_size": 50
}
```

**Response:**
```json
{
  "status": "success",
  "processed": 50,
  "successful": 45,
  "failed": 5,
  "progress": "33%"
}
```

#### `GET /api/geocode/status`
Retrieves the current status of a geocoding operation.

**Request:**
- Query Parameter: `session_id`

**Response:**
```json
{
  "status": "in_progress", 
  "completed": 50,
  "total": 150,
  "percent_complete": 33
}
```

### 3. Analysis API

#### `POST /api/analyze`
Performs income and directional analysis.

**Request:**
```json
{
  "session_id": "abc123def456",
  "reference_point": {
    "address": "123 Main St, Santa Rosa Beach, FL 32459",
    "lat": 30.3960324,
    "lng": -86.2788076
  },
  "directions": ["north", "south", "east", "west"],
  "income_threshold": 500
}
```

**Response:**
```json
{
  "status": "success",
  "analysis_id": "xyz789",
  "stats": {
    "total_records": 150,
    "records_analyzed": 145,
    "income_filtered": 78,
    "direction_filtered": {
      "north": 22,
      "south": 18,
      "east": 25,
      "west": 13
    }
  }
}
```

### 4. Visualization API

#### `GET /api/visualization/map`
Retrieves map data for visualizing properties.

**Request:**
- Query Parameters:
  - `analysis_id`
  - `directions` (optional)
  - `format` (html, json)

**Response:**
```json
{
  "map_data": {
    "center": [30.3960324, -86.2788076],
    "zoom": 12,
    "reference_point": {
      "lat": 30.3960324,
      "lng": -86.2788076,
      "label": "Reference Point"
    },
    "points": [
      {
        "lat": 30.4010324,
        "lng": -86.2718076,
        "direction": "north",
        "income": 750,
        "id": "rec001"
      },
      // Additional points...
    ]
  }
}
```

#### `GET /api/visualization/chart`
Retrieves chart data for income distribution.

**Request:**
- Query Parameters:
  - `analysis_id`
  - `chart_type` (income_distribution, direction_comparison)
  - `format` (svg, json)

**Response:** JSON data structured for chart rendering

### 5. Reporting API

#### `POST /api/reports/generate`
Generates a PDF or CSV report.

**Request:**
```json
{
  "analysis_id": "xyz789",
  "format": "pdf",
  "include_sections": ["map", "statistics", "data_table"],
  "title": "Housing Analysis Report - North Area"
}
```

**Response:**
```json
{
  "status": "success",
  "report_url": "/reports/xyz789/report.pdf",
  "expires_at": "2023-12-31T23:59:59Z"
}
```

## API Authentication

The API uses token-based authentication for secure access:

- All API requests must include an `Authorization` header with a valid token
- Tokens are issued upon initial session creation
- Tokens expire after 24 hours of inactivity

## Error Handling

All API endpoints follow a standard error response format:

```json
{
  "status": "error",
  "code": "GEOCODE_FAILED",
  "message": "Failed to geocode the provided address",
  "details": {
    "address": "123 Invalid St",
    "reason": "Address not found"
  }
}
```

Common error codes:
- `INVALID_INPUT`: Invalid request parameters
- `UPLOAD_FAILED`: CSV upload or processing failed
- `GEOCODE_FAILED`: Address geocoding failed
- `ANALYSIS_ERROR`: Error during analysis
- `REPORT_GENERATION_ERROR`: Error generating report
- `UNAUTHORIZED`: Authentication required or token expired

## Rate Limiting

To ensure optimal performance and fair usage:

- Upload API: 10 requests per hour
- Geocoding API: 1000 addresses per day
- Report Generation: 50 reports per day

## API Integration Examples

### Example: Uploading Data and Running Analysis

```python
import requests

# 1. Upload CSV file
files = {'file': open('donor_data.csv', 'rb')}
upload_response = requests.post('https://housing-analysis-app.example.com/api/upload', 
                               files=files)
session_id = upload_response.json()['session_id']

# 2. Start geocoding process
geocode_response = requests.post('https://housing-analysis-app.example.com/api/geocode',
                               json={'session_id': session_id, 'batch_size': 100})

# 3. Wait for geocoding to complete
while True:
    status_response = requests.get('https://housing-analysis-app.example.com/api/geocode/status',
                                 params={'session_id': session_id})
    status_data = status_response.json()
    if status_data['status'] == 'completed':
        break
    time.sleep(2)  # Poll every 2 seconds

# 4. Run analysis
analysis_response = requests.post('https://housing-analysis-app.example.com/api/analyze',
                                json={
                                    'session_id': session_id,
                                    'reference_point': {
                                        'address': '123 Main St, Santa Rosa Beach, FL 32459'
                                    },
                                    'directions': ['north', 'south', 'east', 'west'],
                                    'income_threshold': 500
                                })
analysis_id = analysis_response.json()['analysis_id']

# 5. Generate and download report
report_response = requests.post('https://housing-analysis-app.example.com/api/reports/generate',
                              json={
                                  'analysis_id': analysis_id,
                                  'format': 'pdf',
                                  'include_sections': ['map', 'statistics', 'data_table']
                              })
report_url = report_response.json()['report_url']
``` 