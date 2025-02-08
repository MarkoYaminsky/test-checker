import io
import os
import uuid

from fpdf import FPDF


def create_grid_pdf(columns_number: int, rows_number: int) -> io.BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    column_width = 10
    row_height = 10

    pdf.cell(column_width, row_height, "", border=1, align="C")
    for column_index in range(columns_number):
        pdf.cell(column_width, row_height, chr(65 + column_index), border=1, align="C")
    pdf.ln()

    for row_index in range(rows_number):
        pdf.cell(column_width, row_height, str(row_index + 1), border=1, align="C")
        for column_index in range(columns_number):
            pdf.cell(column_width, row_height, "", border=1, align="C")
        pdf.ln()

    path = f"{uuid.uuid4()}.pdf"
    pdf.output(path)
    with open(path, "rb") as file:
        output = io.BytesIO(file.read())
    os.remove(path)

    return output
