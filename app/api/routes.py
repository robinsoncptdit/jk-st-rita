from flask import jsonify, request, current_app
from app.api import bp
from app.services.geocoding import GeocodingService
from app.services.analysis import AnalysisService
from app.services.visualization import VisualizationService
from app.services.reporting import ReportingService
from werkzeug.utils import secure_filename
import os

# Initialize services
geocoding_service = None
analysis_service = None
visualization_service = None
reporting_service = None

def get_geocoding_service():
    global geocoding_service
    if geocoding_service is None:
        geocoding_service = GeocodingService()
    return geocoding_service

def get_analysis_service():
    global analysis_service
    if analysis_service is None:
        analysis_service = AnalysisService()
    return analysis_service

def get_visualization_service():
    global visualization_service
    if visualization_service is None:
        visualization_service = VisualizationService()
    return visualization_service

def get_reporting_service():
    global reporting_service
    if reporting_service is None:
        reporting_service = ReportingService()
    return reporting_service

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            current_app.logger.error('No file part in request')
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            current_app.logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400
        
        if not file.filename.endswith('.csv'):
            current_app.logger.error(f'Invalid file type: {file.filename}')
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        if file:
            try:
                # Create upload directory if it doesn't exist
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save the file
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                current_app.logger.info(f'File saved successfully: {file_path}')
                
                # Process the uploaded file
                analysis_service = get_analysis_service()
                result = analysis_service.process_csv(file_path)
                
                if isinstance(result, dict) and result.get('error'):
                    current_app.logger.error(f'Error processing CSV: {result["error"]}')
                    return jsonify({'error': result['error']}), 400
                
                return jsonify({
                    'message': 'File uploaded and processed successfully',
                    'filename': filename,
                    'analysis': result
                }), 200
                
            except Exception as e:
                current_app.logger.error(f'Error handling file upload: {str(e)}')
                return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    except Exception as e:
        current_app.logger.error(f'Unexpected error in upload_file: {str(e)}')
        return jsonify({'error': 'An unexpected error occurred'}), 500

@bp.route('/geocode', methods=['POST'])
def geocode_address():
    """Geocode an address."""
    data = request.get_json()
    if not data or 'address' not in data:
        return jsonify({'error': 'Address is required'}), 400
    
    geocoding_service = get_geocoding_service()
    result = geocoding_service.geocode(data['address'])
    
    if result is None:
        return jsonify({'error': 'Could not geocode address'}), 400
    
    return jsonify(result), 200

@bp.route('/analyze', methods=['POST'])
def analyze_data():
    """Analyze data based on directions and threshold."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    reference_point = data.get('reference_point')
    directions = data.get('directions', [])
    threshold = data.get('threshold')
    
    if not reference_point:
        return jsonify({'error': 'Reference point is required'}), 400
    
    analysis_service = get_analysis_service()
    result = analysis_service.analyze_directions(reference_point, directions)
    
    if threshold is not None:
        filtered_data = analysis_service.filter_by_threshold(threshold)
        result['filtered_data'] = filtered_data
    
    return jsonify(result), 200

@bp.route('/visualization/map', methods=['POST'])
def get_map():
    """Generate map visualization."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    reference_point = data.get('reference_point')
    points = data.get('points', {})
    directions = data.get('directions')
    
    if not reference_point or not points:
        return jsonify({'error': 'Reference point and points are required'}), 400
    
    visualization_service = get_visualization_service()
    map_file = visualization_service.create_map(reference_point, points, directions)
    
    if map_file is None:
        return jsonify({'error': 'Could not generate map'}), 500
    
    return jsonify({'map_file': os.path.basename(map_file)}), 200

@bp.route('/visualization/chart', methods=['POST'])
def get_chart_data():
    """Get data for charts."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    visualization_service = get_visualization_service()
    chart_data = visualization_service.create_chart_data(data)
    
    return jsonify(chart_data), 200

@bp.route('/reports/generate', methods=['POST'])
def generate_report():
    """Generate analysis report."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    format = data.get('format', 'pdf')
    analysis_data = data.get('analysis_data')
    reference_point = data.get('reference_point')
    
    if not analysis_data or not reference_point:
        return jsonify({'error': 'Analysis data and reference point are required'}), 400
    
    reporting_service = get_reporting_service()
    
    if format == 'pdf':
        report_file = reporting_service.generate_pdf_report(analysis_data, reference_point)
    else:
        report_file = reporting_service.generate_csv_report(analysis_data)
    
    if report_file is None:
        return jsonify({'error': f'Could not generate {format.upper()} report'}), 500
    
    return jsonify({'report_file': os.path.basename(report_file)}), 200 