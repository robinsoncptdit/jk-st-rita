import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
from flask import current_app

class AnalysisService:
    def __init__(self):
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
        self.analysis_results = {}
    
    def process_csv(self, filepath: str) -> Dict:
        """Process uploaded CSV file and prepare for analysis."""
        try:
            # Read CSV file
            df = pd.read_csv(filepath)
            
            # Validate required columns
            required_columns = ['address', 'contribution_amount']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Clean and prepare data
            df['address'] = df['address'].str.strip()
            df['contribution_amount'] = pd.to_numeric(df['contribution_amount'], errors='coerce')
            
            # Generate analysis ID
            analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save processed data
            processed_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            df.to_csv(processed_file, index=False)
            
            return {
                'analysis_id': analysis_id,
                'total_records': len(df),
                'valid_addresses': df['address'].notna().sum(),
                'valid_contributions': df['contribution_amount'].notna().sum()
            }
            
        except Exception as e:
            raise Exception(f"Error processing CSV: {str(e)}")
    
    def determine_direction(self, ref_lat: float, ref_lng: float, 
                          point_lat: float, point_lng: float) -> str:
        """Determine cardinal direction between two points."""
        lat_diff = point_lat - ref_lat
        lng_diff = point_lng - ref_lng
        
        # Calculate angle for more precise direction
        angle = np.degrees(np.arctan2(lng_diff, lat_diff))
        
        # Map angle to cardinal direction
        if -45 <= angle <= 45:
            return 'north'
        elif 45 < angle <= 135:
            return 'east'
        elif -135 <= angle < -45:
            return 'west'
        else:
            return 'south'
    
    def analyze(self, reference_point: Dict, directions: List[str], 
                threshold: float = 500) -> Dict:
        """Perform directional and contribution analysis."""
        try:
            # Load processed data
            analysis_id = reference_point.get('analysis_id')
            if not analysis_id:
                raise ValueError("Analysis ID required")
            
            processed_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            if not os.path.exists(processed_file):
                raise FileNotFoundError("Processed data not found")
            
            df = pd.read_csv(processed_file)
            
            # Filter by contribution threshold
            df_filtered = df[df['contribution_amount'] >= threshold].copy()
            
            # Calculate directions for each point
            ref_lat = reference_point['lat']
            ref_lng = reference_point['lng']
            
            df_filtered['direction'] = df_filtered.apply(
                lambda row: self.determine_direction(
                    ref_lat, ref_lng,
                    row['lat'], row['lng']
                ),
                axis=1
            )
            
            # Filter by requested directions
            df_filtered = df_filtered[df_filtered['direction'].isin(directions)]
            
            # Calculate statistics
            stats = {
                'total_records': len(df),
                'records_analyzed': len(df_filtered),
                'income_filtered': len(df[df['contribution_amount'] >= threshold]),
                'direction_filtered': {
                    direction: len(df_filtered[df_filtered['direction'] == direction])
                    for direction in directions
                },
                'contribution_stats': {
                    'mean': df_filtered['contribution_amount'].mean(),
                    'median': df_filtered['contribution_amount'].median(),
                    'min': df_filtered['contribution_amount'].min(),
                    'max': df_filtered['contribution_amount'].max()
                }
            }
            
            # Save analysis results
            self.analysis_results[analysis_id] = {
                'stats': stats,
                'data': df_filtered.to_dict('records'),
                'reference_point': reference_point,
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'analysis_id': analysis_id,
                'stats': stats,
                'record_count': len(df_filtered)
            }
            
        except Exception as e:
            raise Exception(f"Analysis error: {str(e)}")
    
    def get_analysis_results(self, analysis_id: str) -> Optional[Dict]:
        """Retrieve analysis results by ID."""
        return self.analysis_results.get(analysis_id)
    
    def export_data(self, analysis_id: str, format: str = 'csv') -> str:
        """Export analysis results in specified format."""
        results = self.get_analysis_results(analysis_id)
        if not results:
            raise ValueError("Analysis results not found")
        
        df = pd.DataFrame(results['data'])
        export_file = os.path.join(self.upload_folder, f'export_{analysis_id}.{format}')
        
        if format == 'csv':
            df.to_csv(export_file, index=False)
        elif format == 'excel':
            df.to_excel(export_file, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return export_file 