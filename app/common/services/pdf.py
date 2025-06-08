import io
import os
import uuid

from fpdf import FPDF
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.services.db import query_relationship
from app.student_tests.models import Question


async def create_grid_pdf(session: AsyncSession, columns_number: int, rows_number: int, questions: list) -> io.BytesIO:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("Arimo", "", "app/common/fonts/Arimo-Regular.ttf", uni=True)
    pdf.set_font("Arimo", size=12)
    page_width = pdf.w - 2 * pdf.l_margin

    pdf.add_page()
    for idx, question in enumerate(questions, start=1):
        pdf.multi_cell(page_width, 10, f"{idx}. {question.content}")
        pdf.set_x(pdf.l_margin)

        answers = await query_relationship(session, question, [Question.answers])
        for i, answer in enumerate(answers):
            answer_indent = 10
            pdf.set_x(pdf.get_x() + answer_indent)
            pdf.cell(0, 10, f"{chr(97 + i)}) {answer.content}", ln=True)

        pdf.ln(5)

    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    column_width = 10
    row_height = 10

    pdf.cell(column_width, row_height, "", border=1, align="C")
    for column_index in range(columns_number - 1):
        pdf.cell(column_width, row_height, chr(65 + column_index), border=1, align="C")
    pdf.ln()

    for row_index in range(rows_number):
        pdf.cell(column_width, row_height, str(row_index + 1), border=1, align="C")
        for column_index in range(columns_number - 1):
            pdf.cell(column_width, row_height, "", border=1, align="C")
        pdf.ln()

    path = f"{uuid.uuid4()}.pdf"
    pdf.output(path)
    with open(path, "rb") as file:
        output = io.BytesIO(file.read())
    os.remove(path)

    return output
