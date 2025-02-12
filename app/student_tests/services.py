from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.services import move_row_values_to_attributes
from app.common.utilities import get_user_model
from app.student_tests.models import Answer, Question, StudentTestAnswer, Test
from app.student_tests.schemas import AnswerCreateSchema, QuestionCreateSchema

User = get_user_model()


def create_test(session: Session, teacher: User, name: str, questions: list[QuestionCreateSchema]) -> Test:
    test = Test(teacher_id=teacher.id, name=name)
    session.add(test)
    session.commit()

    for index, question in enumerate(questions, start=1):
        create_question(
            session=session,
            test=test,
            position_number=index,
            content=question.content,
            answers=question.answers,
            points=question.points,
        )

    return test


def create_question(
    session: Session,
    test: Test,
    content: str,
    points: int,
    answers: list[AnswerCreateSchema],
    position_number: int | None = None,
) -> Question:
    if position_number is None:
        position_number = len(test.questions) + 1

    question = Question(test_id=test.id, content=content, position_number=position_number, points=points)
    session.add(question)
    session.commit()
    session.refresh(question)

    for index, answer in enumerate(answers, start=1):
        create_answer(
            session=session,
            question=question,
            position_number=index,
            content=answer.content,
            is_correct=answer.is_correct,
        )

    return question


def create_answer(
    session: Session, question: Question, content: str, is_correct: bool, position_number: int | None = None
) -> Answer:
    if position_number is None:
        position_number = len(question.answers) + 1

    answer = Answer(question_id=question.id, content=content, is_correct=is_correct, position_number=position_number)
    session.add(answer)
    session.commit()
    session.refresh(answer)
    return answer


def delete_test(session: Session, test: Test) -> None:
    session.delete(test)
    session.commit()


def delete_question(session: Session, question: Question) -> None:
    session.delete(question)
    session.commit()


def delete_answer(session: Session, answer: Answer) -> None:
    session.delete(answer)
    session.commit()


def update_test(session: Session, test: Test, name: str) -> Test:
    test.name = name
    session.commit()
    session.refresh(test)
    return test


def update_question(session: Session, question: Question, content: str) -> Question:
    question.content = content
    session.commit()
    session.refresh(question)
    return question


def update_answer(session: Session, answer: Answer, content: str, is_correct: bool) -> Answer:
    answer.content = content
    answer.is_correct = is_correct
    session.commit()
    session.refresh(answer)
    return answer


def create_student_answer(session: Session, test: Test, student_username: str, results_url: str) -> StudentTestAnswer:
    answer = StudentTestAnswer(test_id=test.id, student_username=student_username, results_photo_url=results_url)
    session.add(answer)
    session.commit()
    session.refresh(answer)
    # TODO Launch celery task for grading the test
    return answer


def annotate_student_answers_with_test_info(
    session: Session, answers: list[StudentTestAnswer]
) -> list[dict[StudentTestAnswer, str, str]]:
    answer_ids = [answer.id for answer in answers]
    query = (
        select(
            StudentTestAnswer,
            Test.name.label("test_name"),
            func.coalesce(func.sum(Question.points).label("max_points"), 0),
        )
        .select_from(StudentTestAnswer)
        .join(Test)
        .outerjoin(Question)
        .where(StudentTestAnswer.id.in_(answer_ids))
        .group_by(
            StudentTestAnswer.id,
            Test.name,
        )
    )

    return move_row_values_to_attributes(
        session.execute(query).all(),
        (
            "test_name",
            "max_score",
        ),
    )
