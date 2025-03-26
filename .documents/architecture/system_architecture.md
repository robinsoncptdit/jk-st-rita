# Housing & Income Analysis Tool: System Architecture

## Architecture Overview

This document describes the architectural design of the Housing & Income Analysis Tool. The system follows a modular architecture that separates concerns while allowing for efficient data processing and analysis.

## System Architecture Diagram

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Web Browser   │◄────►│  Flask Server   │◄────►│  Geocoding API  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  Map Rendering  │◄────►│ Core Processing │◄────►│  Data Storage   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                ▼
┌─────────────────┐      ┌─────────────────┐
│  PDF Generator  │◄────►│ Analysis Engine │
└─────────────────┘      └─────────────────┘
```

## Component Architecture

### 1. Web Application Layer

The web application layer handles user interactions and provides the interface for data upload, configuration, and results display.

#### Flask Application Structure
```
app/
├── __init__.py         # Application factory pattern
├── routes.py           # URL routing
├── auth.py             # Authentication (if needed)
├── templates/          # Jinja2 templates
└── static/             # Static assets
```

#### Key Design Patterns
- **Model-View-Controller (MVC)**: Separates data, presentation, and logic
- **Application Factory**: Enables flexible application initialization
- **Blueprints**: Organizes routes by functional area

### 2. Data Processing Layer

The data processing layer handles CSV parsing, validation, and transformation.

#### Components
- **CSV Parser**: Processes user-uploaded CSV files
- **Data Validator**: Validates and cleans incoming data
- **Data Transformer**: Prepares data for analysis

#### Design Considerations
- Memory-efficient processing for large files using chunked processing
- Comprehensive validation to handle inconsistent data
- Clear error reporting for invalid records

### 3. Geocoding System

The geocoding system converts addresses to geographic coordinates and handles caching to minimize API usage.

#### Components
- **Geocoder Service**: Interface to geocoding API providers
- **Cache Manager**: Stores and retrieves geocoded results
- **Batch Processor**: Manages batch processing of addresses

#### Design Considerations
- **Service Abstraction**: Allows switching between different geocoding providers
- **Caching Strategy**: Persistent storage of geocoded results to reduce API calls
- **Error Handling**: Robust handling of geocoding failures
- **Rate Limiting**: Respects API usage limits

### 4. Directional Analysis Engine

The directional analysis engine calculates cardinal directions from a reference point and performs filtering based on these directions.

#### Components
- **Direction Calculator**: Determines direction based on coordinates
- **Spatial Filter**: Filters records based on directional criteria
- **Distance Calculator**: Calculates distances between points

#### Algorithms
- **Cardinal Direction Algorithm**:
  ```python
  def determine_direction(ref_lat, ref_lng, point_lat, point_lng):
      lat_diff = point_lat - ref_lat
      lng_diff = point_lng - ref_lng
      
      # Primary directions
      if abs(lat_diff) > abs(lng_diff):
          return "north" if lat_diff > 0 else "south"
      else:
          return "east" if lng_diff > 0 else "west"
      
      # For more granular directions (NE, SW, etc.), use:
      # if lat_diff > 0 and lng_diff > 0:
      #     return "northeast"
      # elif lat_diff > 0 and lng_diff < 0:
      #     return "northwest"
      # ...
  ```

### 5. Income Analysis Engine

The income analysis engine performs statistical analysis on financial data, filtering by thresholds and calculating aggregates.

#### Components
- **Threshold Filter**: Filters records based on income thresholds
- **Statistics Generator**: Calculates summary statistics
- **Comparative Analyzer**: Compares statistics across segments

#### Key Metrics
- Average contribution amount by direction
- Median contribution
- Contribution density by geographic area
- Contribution range and distribution

### 6. Visualization System

The visualization system generates interactive maps and charts to display analysis results.

#### Components
- **Map Generator**: Creates interactive maps using Folium
- **Chart Generator**: Builds statistical charts using Matplotlib/Seaborn
- **Color Scheme Manager**: Manages consistent color coding

#### Technologies
- **Folium**: For interactive maps
- **Matplotlib/Seaborn**: For statistical visualizations
- **D3.js** (optional): For advanced interactive visualizations

### 7. Reporting System

The reporting system generates PDF reports and CSV exports of analysis results.

#### Components
- **Report Template Engine**: Manages report layouts and styling
- **PDF Generator**: Converts analysis results to PDF format
- **CSV Exporter**: Creates downloadable CSV files

## Data Flow

### 1. Data Upload Flow
```
User → Upload CSV → Validation → Preprocessing → Session Storage
```

### 2. Geocoding Flow
```
Addresses → Cache Check → Geocoding API → Coordinate Storage → Validation
```

### 3. Analysis Flow
```
Reference Point → Direction Calculation → Income Filtering → Statistical Analysis → Results Generation
```

### 4. Visualization Flow
```
Analysis Results → Map Generation → Chart Generation → Interactive UI
```

### 5. Reporting Flow
```
Analysis Results → Template Selection → Data Formatting → PDF/CSV Generation → Download
```

## Architectural Decisions

### 1. Why Flask?
Flask was chosen for its lightweight nature, flexibility, and ease of integration with data processing libraries like Pandas and visualization tools like Folium. The application doesn't require complex ORM features or heavy framework components, making Flask an ideal choice.

### 2. In-Memory vs. Database Storage
The application primarily uses in-memory processing with Pandas DataFrame for several reasons:
- Most analysis sessions are short-lived
- The expected dataset size is moderate
- In-memory processing offers better performance for analytical operations

For larger deployments, a database backend could be added to store:
- User accounts
- Cached geocoding results
- Saved analysis sessions

### 3. Geocoding Service Selection
The architecture supports multiple geocoding providers:
- **Nominatim (OpenStreetMap)**: Free, but has usage limits and variable accuracy
- **Google Maps Geocoding API**: More accurate, but has usage costs
- **Mapbox Geocoding API**: Good balance of cost and accuracy

The service abstraction allows switching between providers based on needs and budget constraints.

### 4. Asynchronous Processing
Long-running operations like batch geocoding are designed to run asynchronously to prevent blocking the web interface. This is implemented through:
- Background tasks
- Status polling endpoints
- Progress indicators in the UI

### 5. Security Considerations
The architecture incorporates several security measures:
- CSV validation to prevent injection attacks
- API rate limiting to prevent abuse
- Token-based authentication for API access
- Sanitization of user inputs

## Performance Considerations

### 1. Caching Strategy
- Geocoding results are cached to minimize expensive API calls
- Analysis results are cached for quick retrieval during UI interactions
- Static assets are cached with appropriate headers

### 2. Large Dataset Handling
- Chunked processing for CSV parsing
- Pagination for result display
- Optimization of memory-intensive operations

### 3. Scaling Approach
- Horizontal scaling through stateless application servers
- Shared cache for geocoding results
- Load balancing for multi-user deployments

## Future Architectural Extensions

### 1. Database Integration
For persistent storage of:
- User accounts and preferences
- Analysis history
- Expanded geocoding cache

### 2. Microservices Evolution
As the application grows, components could be separated into microservices:
- Geocoding service
- Analysis service
- Reporting service

### 3. Real-time Collaboration
Adding WebSocket support for:
- Real-time data visualization
- Collaborative analysis sessions
- Live status updates

## Testing Architecture

### 1. Unit Testing
- Component-level tests for each service
- Mocked dependencies for isolated testing

### 2. Integration Testing
- API endpoint tests
- Service interaction tests

### 3. Performance Testing
- Load testing for concurrent uploads
- Performance benchmarks for large datasets
- Stress testing for geocoding capacity 