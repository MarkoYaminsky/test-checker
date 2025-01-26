from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.services import move_row_values_to_attributes
from app.common.utilities import get_user_model
from app.student_tests.models import Answer, Question, StudentTestAnswer, Test
from app.student_tests.schemas import AnswerCreateSchema, QuestionCreateSchema

User = get_user_model()


async def create_test(session: AsyncSession, teacher: User, name: str, questions: list[QuestionCreateSchema]) -> Test:
    test = Test(teacher_id=teacher.id, name=name)
    session.add(test)
    await session.commit()

    for index, question in enumerate(questions, start=1):
        await create_question(
            session=session,
            test=test,
            position_number=index,
            content=question.content,
            answers=question.answers,
            points=question.points,
        )

    return test


async def create_question(
    session: AsyncSession,
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
    await session.commit()
    await session.refresh(question)

    for index, answer in enumerate(answers, start=1):
        await create_answer(
            session=session,
            question=question,
            position_number=index,
            content=answer.content,
            is_correct=answer.is_correct,
        )

    return question


async def create_answer(
    session: AsyncSession, question: Question, content: str, is_correct: bool, position_number: int | None = None
) -> Answer:
    if position_number is None:
        position_number = len(question.answers) + 1

    answer = Answer(question_id=question.id, content=content, is_correct=is_correct, position_number=position_number)
    session.add(answer)
    await session.commit()
    await session.refresh(answer)
    return answer


async def delete_test(session: AsyncSession, test: Test) -> None:
    await session.delete(test)
    await session.commit()


async def delete_question(session: AsyncSession, question: Question) -> None:
    await session.delete(question)
    await session.commit()


async def delete_answer(session: AsyncSession, answer: Answer) -> None:
    await session.delete(answer)
    await session.commit()


async def update_test(session: AsyncSession, test: Test, name: str) -> Test:
    test.name = name
    await session.commit()
    await session.refresh(test)
    return test


async def update_question(session: AsyncSession, question: Question, content: str) -> Question:
    question.content = content
    await session.commit()
    await session.refresh(question)
    return question


async def update_answer(session: AsyncSession, answer: Answer, content: str, is_correct: bool) -> Answer:
    answer.content = content
    answer.is_correct = is_correct
    await session.commit()
    await session.refresh(answer)
    return answer


async def create_student_answer(
    session: AsyncSession, test: Test, student_username: str, results_url: str
) -> StudentTestAnswer:
    answer = StudentTestAnswer(test_id=test.id, student_username=student_username, results_photo_url=results_url)
    session.add(answer)
    await session.commit()
    await session.refresh(answer)
    # TODO Launch celery task for grading the test
    return answer


async def get_student_answers_with_test_info(
    session: AsyncSession, test: Test
) -> list[dict[StudentTestAnswer, str, str]]:
    query = (
        select(
            StudentTestAnswer,
            Test.name.label("test_name"),
            func.coalesce(func.sum(Question.points).label("max_points"), 0),
        )
        .select_from(StudentTestAnswer)
        .join(Test)
        .outerjoin(Question)
        .where(StudentTestAnswer.test_id == test.id)
        .group_by(
            StudentTestAnswer.id,
            Test.name,
        )
    )

    results = await session.execute(query)
    return move_row_values_to_attributes(
        results,
        (
            "test_name",
            "max_score",
        ),
    )
