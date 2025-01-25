from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.student_tests.models import Question


class AnswerOutputSchema(BaseModel):
    id: UUID
    content: str
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


class QuestionOutputSchema(BaseModel):
    id: UUID
    content: str
    position_number: int
    type: Question.Type

    model_config = ConfigDict(from_attributes=True)


class TestOutputSchema(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class AnswerCreateSchema(BaseModel):
    content: str
    is_correct: bool


class QuestionCreateSchema(BaseModel):
    content: str
    type: Question.Type
    points: int
    answers: list[AnswerCreateSchema]


class TestCreateSchema(BaseModel):
    name: str
    questions: list[QuestionCreateSchema] = []


class QuestionUpdateSchema(BaseModel):
    content: str


class AnswerUpdateSchema(BaseModel):
    content: str
    is_correct: bool


class StudentTestAnswerOutputSchema(BaseModel):
    id: UUID
    test_id: UUID
    created_at: datetime
    student_username: str
    results_photo_url: str
    score: int | None

    model_config = ConfigDict(from_attributes=True)
