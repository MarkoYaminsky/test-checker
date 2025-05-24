from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints


class AnswerOutputSchema(BaseModel):
    id: UUID
    content: str
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


class QuestionOutputSchema(BaseModel):
    id: UUID
    content: str
    points: int
    position_number: int

    model_config = ConfigDict(from_attributes=True)


class TestOutputSchema(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    questions_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


class AnswerCreateSchema(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1)]
    is_correct: bool


class QuestionCreateSchema(BaseModel):
    content: Annotated[str, StringConstraints(min_length=3)]
    points: int
    answers: list[AnswerCreateSchema]


class TestCreateSchema(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3)]
    questions: list[QuestionCreateSchema] = []


class TestUpdateSchema(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3)]
    question_ids: list[UUID] = []


class QuestionUpdateSchema(BaseModel):
    content: Annotated[str, StringConstraints(min_length=3)]


class AnswerUpdateSchema(BaseModel):
    content: Annotated[str, StringConstraints(min_length=1)]
    is_correct: bool


class StudentTestAnswerOutputSchema(BaseModel):
    id: UUID
    test_id: UUID
    created_at: datetime
    student_username: str
    results_photo_url: str
    test_name: str
    max_score: int
    score: int | None

    model_config = ConfigDict(from_attributes=True)


class StudentTestAnswerUpdateSchema(BaseModel):
    score: int

    model_config = ConfigDict(from_attributes=True)
