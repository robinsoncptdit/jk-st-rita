from flask import render_template, current_app
from app.main import bp

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload')
def upload():
    return render_template('upload.html')

@bp.route('/analysis')
def analysis():
    return render_template('analysis.html')

@bp.route('/map')
def map_view():
    return render_template('map.html')

@bp.route('/reports')
def reports():
    return render_template('reports.html') 