from flask import render_template, flash, redirect, url_for, current_app, send_from_directory
from app.main import bp
import os

@bp.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@bp.route('/upload')
def upload():
    """Render the upload page."""
    return render_template('upload.html')

@bp.route('/analysis')
def analysis():
    """Render the analysis page."""
    return render_template('analysis.html')

@bp.route('/map')
def map_view():
    """Render the map view page."""
    return render_template('map.html')

@bp.route('/reports')
def reports():
    """Render the reports page."""
    return render_template('reports.html')

@bp.route('/maps/<path:filename>')
def serve_map(filename):
    """Serve generated map files."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/reports/<path:filename>')
def serve_report(filename):
    """Serve generated report files."""
    return send_from_directory(current_app.config['REPORT_FOLDER'], filename) 