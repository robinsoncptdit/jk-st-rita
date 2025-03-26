# Housing & Income Analysis Tool (Python Version)

Thanks for providing the sample data and answering my questions. Now I can refine the project outline with more specific details based on your dataset and requirements.

## Dataset Analysis

Looking at your provided data, I can see it contains:
- Personal information (names, addresses)
- Location data (addresses in Santa Rosa Beach, FL and other locations)
- Financial data (donations, contributions)
- Family/Individual status
- Age information (when available)

The dataset appears to be moderate in size, with each record containing multiple fields. This should be manageable for in-memory processing with Python.

## Refined Technical Stack

- **Backend**: Python with Flask (lightweight and easy to implement)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap for responsive design
- **Data Processing**: Pandas for CSV handling
- **Geospatial Processing**: 
  - Geocoding API: Google Maps Geocoding API or Nominatim (OpenStreetMap)
  - Directional calculations: Custom algorithms using GeoPy
- **Visualization**: 
  - Folium (for interactive maps with OpenStreetMap)
  - Matplotlib/Seaborn (for income distribution charts)
- **PDF Generation**: ReportLab or WeasyPrint for PDF reports

## Core Features (Updated)

1. **CSV Upload & Processing**
   - Parse the CSV format similar to your provided sample
   - Clean and structure data for analysis
   - Handle address parsing and normalization

2. **Geocoding System**
   - Convert addresses to latitude/longitude using Google Maps API or Nominatim
   - Cache geocoded results to minimize API calls
   - Handle geocoding errors gracefully

3. **Directional Analysis**
   - Allow users to specify a reference point (address or coordinates)
   - Filter properties by cardinal direction (east, west, north, south)
   - Calculate distances from reference point

4. **Income Analysis**
   - Dynamic income threshold filtering (default $500 as specified)
   - Statistical analysis of income data by direction
   - Comparative analysis between directional segments

5. **Visualization**
   - Interactive map showing property locations with pins
   - Color-coded pins based on income levels
   - Direction-based highlighting
   - Income distribution charts

6. **Export & Reporting**
   - Screenshot-like PDF generation of analysis results
   - Export filtered data to CSV
   - Summary statistics in downloadable format

## Implementation Details

### Address Geocoding

```python
# Pseudocode for geocoding component
def geocode_addresses(dataframe):
    # Initialize geocoding client (Google Maps or Nominatim)
    geocoder = initialize_geocoder()
    
    # Create cache for geocoded addresses
    geocode_cache = {}
    
    # Process each address
    for index, row in dataframe.iterrows():
        address = f"{row['Address_Line_1']}, {row['City']}, {row['State/Region']} {row['Postal_Code']}"
        
        # Check cache first
        if address in geocode_cache:
            lat, lng = geocode_cache[address]
        else:
            # Call geocoding API
            try:
                result = geocoder.geocode(address)
                lat, lng = result.latitude, result.longitude
                geocode_cache[address] = (lat, lng)
            except Exception as e:
                # Handle geocoding errors
                print(f"Error geocoding address: {address}, {str(e)}")
                lat, lng = None, None
        
        # Add coordinates to dataframe
        dataframe.at[index, 'latitude'] = lat
        dataframe.at[index, 'longitude'] = lng
    
    return dataframe
```

### Directional Filtering

```python
# Pseudocode for directional filtering
def filter_by_direction(dataframe, reference_point, direction):
    ref_lat, ref_lng = reference_point
    
    # Create mask based on direction
    if direction == 'east':
        mask = dataframe['longitude'] > ref_lng
    elif direction == 'west':
        mask = dataframe['longitude'] < ref_lng
    elif direction == 'north':
        mask = dataframe['latitude'] > ref_lat
    elif direction == 'south':
        mask = dataframe['latitude'] < ref_lat
    elif direction == 'northeast':
        mask = (dataframe['longitude'] > ref_lng) & (dataframe['latitude'] > ref_lat)
    # Add other combinations as needed
    
    return dataframe[mask]
```

### Income Threshold Filtering

```python
# Pseudocode for income filtering
def filter_by_income(dataframe, threshold=500):
    # Note: This threshold can be adjusted via user input form
    # Default is 500 as specified
    return dataframe[dataframe['Taxable_Donations_Last_52'] >= threshold]
```

## API Recommendations

1. **Geocoding APIs**:
   - **Google Maps Geocoding API**: Most accurate but has usage costs
   - **Nominatim (OpenStreetMap)**: Free but has usage limits and less accurate in some areas
   - **Mapbox Geocoding API**: Good balance of accuracy and cost

2. **Mapping APIs**:
   - **Folium with OpenStreetMap**: Free, open-source, works well with Python
   - **Google Maps JavaScript API**: More features but has usage costs
   - **Mapbox GL JS**: Good for custom styling and interactive features

3. **PDF Generation**:
   - **ReportLab**: Powerful Python library for PDF generation
   - **WeasyPrint**: Converts HTML/CSS to PDF
   - **pdfkit with wkhtmltopdf**: Converts HTML to PDF using webkit

## Project Structure (Updated)

```
housing-analysis-app/
├── app/
│   ├── __init__.py                # Flask application initialization
│   ├── routes.py                  # Web routes
│   ├── services/
│   │   ├── csv_handler.py         # CSV parsing
│   │   ├── geocoder.py            # Address geocoding
│   │   ├── direction_analyzer.py  # Directional analysis
│   │   ├── income_analyzer.py     # Income analysis
│   │   └── pdf_generator.py       # PDF report generation
│   ├── static/
│   │   ├── css/                   # Stylesheets
│   │   ├── js/                    # Client-side JavaScript
│   │   └── images/                # Images and icons
│   └── templates/                 # HTML templates
├── config.py                      # Configuration settings
├── requirements.txt               # Dependencies
├── run.py                         # Application entry point
└── README.md                      # Documentation
```

## User Interface Flow

1. **Upload Screen**:
   - CSV file upload area
   - Sample data format instructions
   - Upload button

2. **Analysis Configuration**:
   - Reference point input (address search box)
   - Direction selection (checkboxes or dropdown)
   - Income threshold input (text box with default value of 500)
   - Analysis button

3. **Results Dashboard**:
   - Interactive map with property pins
   - Income statistics panel
   - Directional breakdown
   - Export options (PDF, CSV)

4. **PDF Report**:
   - Screenshot-like capture of the dashboard
   - Summary statistics
   - Map visualization
   - Filtered data table

## Implementation Plan

1. **Phase 1: Data Processing (1-2 weeks)**
   - Set up Flask application structure
   - Implement CSV parsing with Pandas
   - Create data validation and cleaning functions

2. **Phase 2: Geocoding System (1-2 weeks)**
   - Implement address geocoding
   - Set up caching system
   - Create coordinate-based calculations

3. **Phase 3: Analysis Features (1-2 weeks)**
   - Implement directional filtering
   - Create income analysis functions
   - Build statistical calculations

4. **Phase 4: Visualization (1-2 weeks)**
   - Implement map visualization with Folium
   - Create income distribution charts
   - Build interactive filtering controls

5. **Phase 5: Reporting & Export (1 week)**
   - Implement PDF generation
   - Create CSV export functionality
   - Build summary report templates

6. **Phase 6: Testing & Refinement (1 week)**
   - Test with various datasets
   - Optimize performance
   - Refine user interface

## Next Steps

1. Set up the Python development environment with Flask and required packages
2. Create a basic CSV parser to handle the specific format of your data
3. Implement a prototype of the geocoding system
4. Build a simple web interface for uploading and configuring analysis

Would you like me to focus on any specific aspect of this plan in more detail? Or would you prefer to see some initial code for a particular component?