import folium
from folium import plugins
from typing import Dict, List, Optional
import pandas as pd
from flask import current_app
import os

class VisualizationService:
    def __init__(self):
        self._upload_folder = None
        self._df = None
    
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
    
    def create_map(self, center_point: Dict[str, float], points: List[Dict], 
                  directions: Optional[List[str]] = None) -> str:
        """Create an interactive map visualization."""
        try:
            # Create base map centered on reference point
            m = folium.Map(
                location=[center_point['latitude'], center_point['longitude']],
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Add reference point
            folium.Marker(
                [center_point['latitude'], center_point['longitude']],
                popup='Reference Point',
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            # Add direction-based points
            colors = {
                'north': 'blue',
                'south': 'green',
                'east': 'purple',
                'west': 'orange'
            }
            
            for direction, points_list in points.items():
                if directions and direction not in directions:
                    continue
                    
                for point in points_list:
                    folium.CircleMarker(
                        location=[point['latitude'], point['longitude']],
                        radius=8,
                        popup=f"Address: {point['address']}<br>Contribution: ${point['contribution']:,.2f}",
                        color=colors.get(direction, 'gray'),
                        fill=True,
                        fill_color=colors.get(direction, 'gray')
                    ).add_to(m)
            
            # Add legend
            legend_html = '''
                <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
                    <h4>Legend</h4>
                    <div><i class="fa fa-circle" style="color: red"></i> Reference Point</div>
            '''
            for direction in directions or []:
                color = colors.get(direction, 'gray')
                legend_html += f'<div><i class="fa fa-circle" style="color: {color}"></i> {direction.capitalize()}</div>'
            legend_html += '</div>'
            m.get_root().html.add_child(folium.Element(legend_html))
            
            # Save map to a temporary file
            map_file = os.path.join(self.upload_folder, 'temp_map.html')
            m.save(map_file)
            
            return map_file
            
        except Exception as e:
            current_app.logger.error(f"Error creating map visualization: {str(e)}")
            return None
    
    def create_chart_data(self, data: Dict) -> Dict:
        """Create data for charts."""
        try:
            chart_data = {
                'directions': {
                    'labels': [],
                    'counts': [],
                    'totals': [],
                    'averages': []
                }
            }
            
            for direction, stats in data['statistics'].items():
                chart_data['directions']['labels'].append(direction.capitalize())
                chart_data['directions']['counts'].append(stats['count'])
                chart_data['directions']['totals'].append(stats['total'])
                chart_data['directions']['averages'].append(stats['average'])
            
            return chart_data
            
        except Exception as e:
            current_app.logger.error(f"Error creating chart data: {str(e)}")
            return {}
    
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