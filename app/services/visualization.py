import folium
from folium import plugins
from typing import Dict, List
import pandas as pd
from flask import current_app
import os

class VisualizationService:
    def __init__(self):
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
    
    def generate_map_data(self, analysis_id: str) -> Dict:
        """Generate map data for visualization."""
        try:
            # Load analysis results
            results_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            if not os.path.exists(results_file):
                raise FileNotFoundError("Analysis results not found")
            
            df = pd.read_csv(results_file)
            
            # Get reference point
            ref_point = df.iloc[0]  # Assuming first row is reference point
            
            # Create base map centered on reference point
            m = folium.Map(
                location=[ref_point['lat'], ref_point['lng']],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Add reference point marker
            folium.Marker(
                [ref_point['lat'], ref_point['lng']],
                popup='Reference Point',
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Add data points with different colors for each direction
            direction_colors = {
                'north': 'blue',
                'south': 'green',
                'east': 'orange',
                'west': 'purple'
            }
            
            # Create feature groups for each direction
            direction_groups = {
                direction: folium.FeatureGroup(name=direction.capitalize())
                for direction in direction_colors.keys()
            }
            
            # Add markers for each data point
            for _, row in df.iterrows():
                if row['direction'] in direction_colors:
                    folium.CircleMarker(
                        location=[row['lat'], row['lng']],
                        radius=8,
                        color=direction_colors[row['direction']],
                        fill=True,
                        popup=f"Amount: ${row['contribution_amount']:.2f}",
                        tooltip=row['address']
                    ).add_to(direction_groups[row['direction']])
            
            # Add all feature groups to map
            for group in direction_groups.values():
                group.add_to(m)
            
            # Add layer control
            folium.LayerControl().add_to(m)
            
            # Add fullscreen option
            plugins.Fullscreen().add_to(m)
            
            # Save map
            map_file = os.path.join(self.upload_folder, f'map_{analysis_id}.html')
            m.save(map_file)
            
            # Generate map data for API response
            map_data = {
                'center': [ref_point['lat'], ref_point['lng']],
                'zoom': 12,
                'reference_point': {
                    'lat': ref_point['lat'],
                    'lng': ref_point['lng'],
                    'label': 'Reference Point'
                },
                'points': [
                    {
                        'lat': row['lat'],
                        'lng': row['lng'],
                        'direction': row['direction'],
                        'contribution': row['contribution_amount'],
                        'address': row['address']
                    }
                    for _, row in df.iterrows()
                    if row['direction'] in direction_colors
                ],
                'map_url': f'/maps/{os.path.basename(map_file)}'
            }
            
            return map_data
            
        except Exception as e:
            raise Exception(f"Map generation error: {str(e)}")
    
    def generate_chart_data(self, analysis_id: str, chart_type: str = 'income_distribution') -> Dict:
        """Generate data for statistical charts."""
        try:
            # Load analysis results
            results_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            if not os.path.exists(results_file):
                raise FileNotFoundError("Analysis results not found")
            
            df = pd.read_csv(results_file)
            
            if chart_type == 'income_distribution':
                # Calculate income distribution by direction
                distribution = df.groupby('direction')['contribution_amount'].agg([
                    'count',
                    'mean',
                    'median',
                    'min',
                    'max'
                ]).to_dict()
                
                return {
                    'type': 'income_distribution',
                    'data': distribution
                }
            
            elif chart_type == 'direction_comparison':
                # Count of contributions by direction
                direction_counts = df['direction'].value_counts().to_dict()
                
                return {
                    'type': 'direction_comparison',
                    'data': direction_counts
                }
            
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
            
        except Exception as e:
            raise Exception(f"Chart generation error: {str(e)}")
    
    def generate_heatmap(self, analysis_id: str) -> Dict:
        """Generate heatmap data for contribution density."""
        try:
            # Load analysis results
            results_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            if not os.path.exists(results_file):
                raise FileNotFoundError("Analysis results not found")
            
            df = pd.read_csv(results_file)
            
            # Prepare heatmap data
            heat_data = [
                [row['lat'], row['lng'], row['contribution_amount']]
                for _, row in df.iterrows()
            ]
            
            return {
                'type': 'heatmap',
                'data': heat_data
            }
            
        except Exception as e:
            raise Exception(f"Heatmap generation error: {str(e)}") 