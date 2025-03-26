import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os
from flask import current_app

class AnalysisService:
    def __init__(self):
        self._upload_folder = None
        self._df = None
        self.analysis_results = {}
    
    @property
    def upload_folder(self):
        if self._upload_folder is None:
            with current_app.app_context():
                self._upload_folder = current_app.config['UPLOAD_FOLDER']
        return self._upload_folder
    
    def load_data(self, filename: str) -> bool:
        """Load data from CSV file."""
        try:
            file_path = os.path.join(self.upload_folder, filename)
            self._df = pd.read_csv(file_path)
            return True
        except Exception as e:
            current_app.logger.error(f"Error loading data: {str(e)}")
            return False
    
    def analyze_directions(self, reference_point: Dict[str, float], directions: List[str]) -> Dict:
        """Analyze data based on cardinal directions from reference point."""
        if self._df is None:
            return {'error': 'No data loaded'}
        
        try:
            # Initialize results
            points = []
            direction_counts = {
                'north': 0,
                'south': 0,
                'east': 0,
                'west': 0
            }
            
            # Process each record
            for _, row in self._df.iterrows():
                # Get direction based on reference point
                direction = self.determine_direction(
                    reference_point['lat'],
                    reference_point['lng'],
                    float(row['latitude']),
                    float(row['longitude'])
                )
                
                if direction in directions:
                    # Add point to results
                    points.append({
                        'lat': float(row['latitude']),
                        'lng': float(row['longitude']),
                        'direction': direction,
                        'contribution': float(row['contribution_amount']),
                        'display_name': row['display_name']
                    })
                    direction_counts[direction] += 1
            
            # Calculate contribution statistics
            contributions = [p['contribution'] for p in points]
            contribution_stats = {
                'mean': float(np.mean(contributions)) if contributions else 0,
                'median': float(np.median(contributions)) if contributions else 0,
                'min': float(min(contributions)) if contributions else 0,
                'max': float(max(contributions)) if contributions else 0,
                'sum': float(sum(contributions)) if contributions else 0
            }
            
            # Prepare statistics
            stats = {
                'total_records': len(self._df),
                'records_analyzed': len(points),
                'income_filtered': len([p for p in points if p['contribution'] >= reference_point.get('threshold', 0)]),
                'direction_filtered': direction_counts,
                'contribution_stats': contribution_stats
            }
            
            return {
                'reference_point': reference_point,
                'points': points,
                'stats': stats
            }
            
        except Exception as e:
            current_app.logger.error(f"Error analyzing directions: {str(e)}")
            return {'error': str(e)}
    
    def filter_by_threshold(self, threshold: float) -> List[Dict]:
        """Filter data by contribution threshold."""
        if self._df is None:
            return []
        
        try:
            filtered_df = self._df[self._df['contribution'] >= threshold]
            return filtered_df.to_dict('records')
        except Exception as e:
            current_app.logger.error(f"Error filtering by threshold: {str(e)}")
            return []
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for the loaded data."""
        if self._df is None:
            return {}
        
        try:
            stats = {
                'total_records': len(self._df),
                'total_contribution': self._df['contribution'].sum(),
                'average_contribution': self._df['contribution'].mean(),
                'median_contribution': self._df['contribution'].median(),
                'min_contribution': self._df['contribution'].min(),
                'max_contribution': self._df['contribution'].max()
            }
            return stats
        except Exception as e:
            current_app.logger.error(f"Error calculating summary statistics: {str(e)}")
            return {}
    
    def process_csv(self, filepath: str) -> Dict:
        """Process uploaded CSV file and prepare for analysis."""
        try:
            # Read CSV file with string type for all columns initially
            df = pd.read_csv(filepath, dtype=str, na_values=[''], keep_default_na=True)
            
            # Validate required columns
            required_columns = [
                'dp_RecordID', 'HOH_Titles', 'Family_Name', 'Address_Line_1', 'City', 
                'State/Region', 'Postal_Code', 'Taxable_Donations_Last_52',
                'CSA_Last_Year', 'Offertory_Rolling_52'
            ]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Clean and prepare data
            # Fill NaN values with appropriate defaults
            df['Address_Line_2'] = df['Address_Line_2'].fillna('')
            
            # Function to clean currency strings and convert to float
            def clean_currency(x):
                if pd.isna(x) or x == '':
                    return 0.0
                try:
                    # Remove currency symbols, spaces, and commas, then convert to float
                    return float(str(x).replace('$', '').replace(',', '').strip())
                except:
                    return 0.0
            
            # Clean and convert contribution columns
            contribution_columns = ['Taxable_Donations_Last_52', 'CSA_Last_Year', 'Offertory_Rolling_52']
            for col in contribution_columns:
                df[col] = df[col].apply(clean_currency)
            
            # Ensure address components are strings and clean them
            address_columns = ['Address_Line_1', 'Address_Line_2', 'City', 'State/Region', 'Postal_Code']
            for col in address_columns:
                df[col] = df[col].astype(str).replace('nan', '').str.strip()
            
            # Combine address components into a single address field
            df['address'] = df.apply(
                lambda row: ', '.join(filter(None, [
                    str(row['Address_Line_1']).strip(),
                    str(row['Address_Line_2']).strip() if row['Address_Line_2'] else '',
                    str(row['City']).strip(),
                    str(row['State/Region']).strip(),
                    str(row['Postal_Code']).split('-')[0].strip()  # Use base ZIP without +4
                ])),
                axis=1
            )
            
            # Calculate total contribution
            df['contribution_amount'] = df[contribution_columns].sum(axis=1)
            
            # Create display name using HOH_Titles + Family_Name
            df['HOH_Titles'] = df['HOH_Titles'].fillna('').astype(str)
            df['Family_Name'] = df['Family_Name'].fillna('').astype(str)
            df['display_name'] = df.apply(
                lambda row: f"{row['HOH_Titles']} {row['Family_Name']}".strip(),
                axis=1
            )
            
            # Function to convert numpy types to Python native types
            def convert_to_native(value):
                if isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
                    return int(value)
                elif isinstance(value, (np.float64, np.float32)):
                    return float(value)
                return value
            
            # Add family information
            df['family_info'] = df.apply(
                lambda row: {
                    'record_id': str(row['dp_RecordID']),
                    'display_name': row['display_name'],
                    'family_name': str(row['Family_Name']),
                    'head_1_name': str(row['Head_1_Name']) if pd.notna(row['Head_1_Name']) else '',
                    'head_2_name': str(row['Head_2_Name']) if pd.notna(row['Head_2_Name']) else '',
                    'salutation': str(row['Salutation']) if pd.notna(row['Salutation']) else '',
                    'formal_addressee': str(row['Formal_Addressee']) if pd.notna(row['Formal_Addressee']) else '',
                    'contributions': {
                        'taxable_donations': convert_to_native(row['Taxable_Donations_Last_52']),
                        'csa': convert_to_native(row['CSA_Last_Year']),
                        'offertory': convert_to_native(row['Offertory_Rolling_52'])
                    }
                },
                axis=1
            )
            
            # Generate analysis ID
            analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save processed data
            processed_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            
            # Convert contribution_amount to native Python float
            df['contribution_amount'] = df['contribution_amount'].apply(convert_to_native)
            
            # Select and save relevant columns
            processed_df = pd.DataFrame({
                'address': df['address'],
                'contribution_amount': df['contribution_amount'],
                'display_name': df['display_name'],
                'family_info': df['family_info'].apply(json.dumps)
            })
            processed_df.to_csv(processed_file, index=False)
            
            # Convert numeric values to native Python types for the return dictionary
            return {
                'analysis_id': analysis_id,
                'total_records': int(len(df)),
                'valid_addresses': int(df['address'].notna().sum()),
                'valid_contributions': int(df['contribution_amount'].notna().sum()),
                'total_contribution': float(df['contribution_amount'].sum()),
                'contribution_summary': {
                    'taxable_donations': float(df['Taxable_Donations_Last_52'].sum()),
                    'csa': float(df['CSA_Last_Year'].sum()),
                    'offertory': float(df['Offertory_Rolling_52'].sum())
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Error in process_csv: {str(e)}")
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