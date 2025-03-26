from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, List, Optional
import pandas as pd
import os
from datetime import datetime

class ReportingService:
    def __init__(self):
        self._report_folder = None
        self._upload_folder = None
        self._df = None
        self.styles = getSampleStyleSheet()
    
    @property
    def report_folder(self):
        if self._report_folder is None:
            with current_app.app_context():
                self._report_folder = current_app.config['REPORT_FOLDER']
        return self._report_folder
    
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
    
    def generate_pdf_report(self, analysis_data: Dict, reference_point: Dict) -> str:
        """Generate a PDF report with analysis results."""
        try:
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(self.report_folder, f'analysis_report_{timestamp}.pdf')
            
            # Create the PDF document
            doc = SimpleDocTemplate(report_file, pagesize=letter)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                spaceAfter=30
            )
            story.append(Paragraph("Housing & Income Analysis Report", title_style))
            story.append(Spacer(1, 20))
            
            # Reference Point
            story.append(Paragraph("Reference Point", self.styles['Heading2']))
            ref_point_text = f"Latitude: {reference_point['latitude']:.6f}, Longitude: {reference_point['longitude']:.6f}"
            story.append(Paragraph(ref_point_text, self.styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Directional Analysis
            story.append(Paragraph("Directional Analysis", self.styles['Heading2']))
            
            for direction, stats in analysis_data['statistics'].items():
                story.append(Paragraph(direction.capitalize(), self.styles['Heading3']))
                data = [
                    ['Metric', 'Value'],
                    ['Count', str(stats['count'])],
                    ['Total Contribution', f"${stats['total']:,.2f}"],
                    ['Average Contribution', f"${stats['average']:,.2f}"],
                    ['Median Contribution', f"${stats['median']:,.2f}"]
                ]
                
                table = Table(data, colWidths=[200, 200])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Build the PDF
            doc.build(story)
            return report_file
            
        except Exception as e:
            current_app.logger.error(f"Error generating PDF report: {str(e)}")
            return None
    
    def generate_csv_report(self, analysis_data: Dict) -> str:
        """Generate a CSV report with analysis results."""
        try:
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(self.report_folder, f'analysis_report_{timestamp}.csv')
            
            # Prepare data for CSV
            rows = []
            for direction, points in analysis_data['points'].items():
                for point in points:
                    rows.append({
                        'Direction': direction.capitalize(),
                        'Address': point['address'],
                        'Latitude': point['latitude'],
                        'Longitude': point['longitude'],
                        'Contribution': point['contribution']
                    })
            
            # Create DataFrame and save to CSV
            df = pd.DataFrame(rows)
            df.to_csv(report_file, index=False)
            
            return report_file
            
        except Exception as e:
            current_app.logger.error(f"Error generating CSV report: {str(e)}")
            return None
    
    def generate_report(self, analysis_id: str, format: str = 'pdf',
                       include_sections: List[str] = None) -> str:
        """Generate a PDF report of the analysis results."""
        try:
            # Load analysis results
            results_file = os.path.join(self.upload_folder, f'processed_{analysis_id}.csv')
            if not os.path.exists(results_file):
                raise FileNotFoundError("Analysis results not found")
            
            df = pd.read_csv(results_file)
            
            # Create report filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(self.report_folder, f'report_{analysis_id}_{timestamp}.pdf')
            
            # Create PDF document
            doc = SimpleDocTemplate(
                report_file,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Container for the 'Flowable' objects
            elements = []
            
            # Styles
            title_style = self.styles['Heading1']
            heading_style = self.styles['Heading2']
            normal_style = self.styles['Normal']
            
            # Title
            elements.append(Paragraph("Housing & Income Analysis Report", title_style))
            elements.append(Spacer(1, 12))
            
            # Report metadata
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            elements.append(Paragraph(f"Analysis ID: {analysis_id}", normal_style))
            elements.append(Spacer(1, 12))
            
            # Summary Statistics
            if 'statistics' in include_sections:
                elements.append(Paragraph("Summary Statistics", heading_style))
                elements.append(Spacer(1, 12))
                
                stats_data = [
                    ['Total Records', str(len(df))],
                    ['Valid Addresses', str(df['address'].notna().sum())],
                    ['Valid Contributions', str(df['contribution_amount'].notna().sum())],
                    ['Average Contribution', f"${df['contribution_amount'].mean():.2f}"],
                    ['Median Contribution', f"${df['contribution_amount'].median():.2f}"],
                    ['Min Contribution', f"${df['contribution_amount'].min():.2f}"],
                    ['Max Contribution', f"${df['contribution_amount'].max():.2f}"]
                ]
                
                stats_table = Table(stats_data, colWidths=[2*inch, 2*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(stats_table)
                elements.append(Spacer(1, 12))
            
            # Directional Analysis
            if 'directional_analysis' in include_sections:
                elements.append(Paragraph("Directional Analysis", heading_style))
                elements.append(Spacer(1, 12))
                
                direction_stats = df.groupby('direction')['contribution_amount'].agg([
                    'count',
                    'mean',
                    'median',
                    'sum'
                ]).round(2)
                
                direction_data = [['Direction', 'Count', 'Average', 'Median', 'Total']]
                for direction, stats in direction_stats.iterrows():
                    direction_data.append([
                        direction.capitalize(),
                        str(stats['count']),
                        f"${stats['mean']:.2f}",
                        f"${stats['median']:.2f}",
                        f"${stats['sum']:.2f}"
                    ])
                
                direction_table = Table(direction_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                direction_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(direction_table)
                elements.append(Spacer(1, 12))
            
            # Data Table
            if 'data_table' in include_sections:
                elements.append(Paragraph("Detailed Data", heading_style))
                elements.append(Spacer(1, 12))
                
                # Prepare data for table
                table_data = [['Address', 'Direction', 'Contribution']]
                for _, row in df.iterrows():
                    table_data.append([
                        row['address'],
                        row['direction'].capitalize(),
                        f"${row['contribution_amount']:.2f}"
                    ])
                
                # Create table with alternating row colors
                data_table = Table(table_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 12),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(data_table)
            
            # Build PDF
            doc.build(elements)
            
            return f'/reports/{os.path.basename(report_file)}'
            
        except Exception as e:
            raise Exception(f"Report generation error: {str(e)}")
    
    def generate_summary_report(self, analysis_id: str) -> str:
        """Generate a concise summary report."""
        return self.generate_report(
            analysis_id,
            include_sections=['statistics', 'directional_analysis']
        )
    
    def generate_detailed_report(self, analysis_id: str) -> str:
        """Generate a detailed report with all sections."""
        return self.generate_report(
            analysis_id,
            include_sections=['statistics', 'directional_analysis', 'data_table']
        ) 