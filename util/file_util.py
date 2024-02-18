import streamlit as st
import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import base64
from io import BytesIO

def create_pdf(dataframe, file_name):
    """Create a PDF file from a DataFrame."""
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Convert DataFrame to a list of lists
    data = [dataframe.columns.tolist()] + dataframe.values.tolist()

    # Create a Table with ReportLab and add style
    table = Table(data)
    table.setStyle(TableStyle([
       ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
       ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
       ('ALIGN',(0,0),(-1,-1),'CENTER'),
       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
       ('BACKGROUND',(0,1),(-1,-1),colors.beige),
       ('GRID',(0,0),(-1,-1), 1, colors.black)
    ]))
    elements.append(table)

    pdf.build(elements)
    buffer.seek(0)

    # Save the PDF to a file
    with open(file_name, 'wb') as f:
        f.write(buffer.read())