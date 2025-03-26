from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from typing import Dict, List
import pandas as pd
from flask import current_app
import os
from datetime import datetime

class ReportingService:
    def __init__(self):
        self.report_folder = current_app.config['REPORT_FOLDER']
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
    
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
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            
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