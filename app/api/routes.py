from flask import jsonify, request, current_app
from app.api import bp
from app.services.geocoding import GeocodingService
from app.services.analysis import AnalysisService
from app.services.visualization import VisualizationService
from app.services.reporting import ReportingService
from werkzeug.utils import secure_filename
import os

# Initialize services
geocoding_service = GeocodingService()
analysis_service = AnalysisService()
visualization_service = VisualizationService()
reporting_service = ReportingService()

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Process the CSV file
    try:
        result = analysis_service.process_csv(filepath)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/geocode', methods=['POST'])
def geocode_addresses():
    data = request.get_json()
    if not data or 'addresses' not in data:
        return jsonify({'error': 'No addresses provided'}), 400
    
    try:
        result = geocoding_service.geocode_batch(data['addresses'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/analyze', methods=['POST'])
def analyze_data():
    data = request.get_json()
    if not data or 'reference_point' not in data:
        return jsonify({'error': 'Reference point required'}), 400
    
    try:
        result = analysis_service.analyze(
            reference_point=data['reference_point'],
            directions=data.get('directions', ['north', 'south', 'east', 'west']),
            threshold=data.get('threshold', 500)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/visualization/map', methods=['GET'])
def get_map_data():
    analysis_id = request.args.get('analysis_id')
    if not analysis_id:
        return jsonify({'error': 'Analysis ID required'}), 400
    
    try:
        map_data = visualization_service.generate_map_data(analysis_id)
        return jsonify(map_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/generate', methods=['POST'])
def generate_report():
    data = request.get_json()
    if not data or 'analysis_id' not in data:
        return jsonify({'error': 'Analysis ID required'}), 400
    
    try:
        report_url = reporting_service.generate_report(
            analysis_id=data['analysis_id'],
            format=data.get('format', 'pdf'),
            include_sections=data.get('include_sections', ['map', 'statistics', 'data_table'])
        )
        return jsonify({'report_url': report_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500 