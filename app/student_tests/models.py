import enum

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.common.models import BaseDatabaseModel
from app.common.utilities import get_user_model

User = get_user_model()


class Test(BaseDatabaseModel):
    __tablename__ = "tests"

    teacher_id = Column(UUID, ForeignKey(User.id), nullable=False)
    name = Column(String, nullable=False)

    teacher = relationship(User, foreign_keys=[teacher_id], back_populates="tests")
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    student_test_answers = relationship("StudentTestAnswer", back_populates="test", cascade="all, delete-orphan")


class Question(BaseDatabaseModel):
    __tablename__ = "test_questions"

    class Type(enum.Enum):
        MULTIPLE_CHOICE = "multiple_choice"
        TRUE_FALSE = "true_false"

    test_id = Column(UUID, ForeignKey(Test.id), nullable=False)
    content = Column(String, nullable=False)
    position_number = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    points = Column(Integer, nullable=True)

    test = relationship(Test, foreign_keys=[test_id], back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("test_id", "position_number", name="uix_test_questions_test_id_number"),)


class Answer(BaseDatabaseModel):
    __tablename__ = "test_answers"

    question_id = Column(UUID, ForeignKey(Question.id), nullable=False)
    content = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    position_number = Column(Integer, nullable=False)

    question = relationship(Question, foreign_keys=[question_id], back_populates="answers")

    __table_args__ = (UniqueConstraint("question_id", "position_number", name="uix_test_answers_question_id_number"),)


# TODO Add celery task for cleaning answers after 1 month
class StudentTestAnswer(BaseDatabaseModel):
    __tablename__ = "student_test_answers"

    test_id = Column(UUID, ForeignKey(Test.id), nullable=False)
    student_username = Column(String, nullable=False)
    results_photo_url = Column(String, nullable=False)
    score = Column(Integer, nullable=True)

    test = relationship(Test, foreign_keys=[test_id], back_populates="student_test_answers")
