import io
from collections import defaultdict
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.services.db import (
    move_row_values_to_attributes,
    query_relationship,
    quick_select,
)
from app.common.services.pdf import create_grid_pdf
from app.common.utilities import get_user_model
from app.student_tests.exceptions import DuplicateTestNameException
from app.student_tests.models import Answer, Question, StudentTestAnswer, Test
from app.student_tests.schemas import AnswerCreateSchema, QuestionCreateSchema
from app.student_tests.tasks import grade_test

User = get_user_model()


async def create_test(session: AsyncSession, teacher: User, name: str, questions: list[QuestionCreateSchema]) -> Test:
    teacher_test_with_same_name = (
        await quick_select(session=session, model=Test, filter_by={"name": name, "teacher_id": teacher.id})
    ).scalar()
    if teacher_test_with_same_name is not None:
        raise DuplicateTestNameException(name)
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
        position_number = (
            len(await query_relationship(session=session, instance=test, relationship_attributes=[Test.questions])) + 1
        )

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
        position_number = len(await query_relationship(session, question, [Question.answers])) + 1

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


async def update_test(session: AsyncSession, test: Test, name: str, question_ids: list[UUID]) -> Test:
    if question_ids:
        ids_to_questions: dict[UUID, Question] = {
            question.id: question
            for question in await query_relationship(
                session=session, instance=test, relationship_attributes=[Test.questions]
            )
        }

        for question in ids_to_questions.values():
            question.position_number += 10000
        await session.flush()

        for index, question_id in enumerate(question_ids, start=1):
            ids_to_questions[question_id].position_number = index

    test.name = name
    await session.commit()
    await session.refresh(test)
    return test


async def update_question(session: AsyncSession, question: Question, content: str, points: int) -> Question:
    question.points = points
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
    session: AsyncSession, test: Test, student_username: str, results_url: str, student_group: str
) -> StudentTestAnswer:
    answer = StudentTestAnswer(
        test_id=test.id, student_username=student_username, results_photo_url=results_url, student_group=student_group
    )
    session.add(answer)
    await session.commit()
    await session.refresh(answer)
    grade_test.delay(test.id, answer.id)
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
        .order_by(StudentTestAnswer.created_at.desc())
    )

    return move_row_values_to_attributes(
        await session.execute(query),
        (
            "test_name",
            "max_score",
        ),
    )


async def annotate_student_answer_with_test_info(
    session: AsyncSession, student_answer: StudentTestAnswer
) -> StudentTestAnswer:
    query = (
        select(
            StudentTestAnswer,
            Test.name.label("test_name"),
            func.coalesce(func.sum(Question.points).label("max_points"), 0),
        )
        .select_from(StudentTestAnswer)
        .join(Test)
        .outerjoin(Question)
        .where(StudentTestAnswer.id == student_answer.id)
        .group_by(
            StudentTestAnswer.id,
            Test.name,
        )
    )

    stmt = await session.execute(query)
    result = stmt.first()
    answer, test_name, max_points = result
    student_answer.test_name = test_name
    student_answer.max_score = max_points
    return student_answer


async def calculate_score_by_answers_grid(session: AsyncSession, grid: dict[int, list[int]], test: Test) -> int:
    answers_query = (
        select(Answer, Question)
        .select_from(Answer)
        .join(Question)
        .where(Question.test_id == test.id, Answer.is_correct.is_(True))
    )

    results = list(await session.execute(answers_query))
    question_position_to_question = {question.position_number: question for _, question in results}
    correct_answers = defaultdict(list)
    for answer, question in results:
        correct_answers[question.position_number].append(answer.position_number)

    score = 0
    for question_number, answers in grid.items():
        if correct_answers[question_number] == answers:
            question = question_position_to_question.get(question_number)
            score += question and question.points or 0

    return score


async def generate_test_answers_grid(session: AsyncSession, test: Test) -> io.BytesIO:
    subquery = (
        select(func.count(Answer.id)).where(Answer.question_id == Question.id).correlate(Question).scalar_subquery()
    )

    query = (
        select(func.count(distinct(Question.id)), func.max(subquery))
        .select_from(Answer)
        .join(Question)
        .where(Question.test_id == test.id)
    )
    result = await session.execute(query)
    max_answer_position, question_count = result.first()
    return await create_grid_pdf(
        session,
        question_count or 0,
        max_answer_position or 0,
        await query_relationship(session, test, [Test.questions]),
    )


async def annotate_tests_with_questions_count(session: AsyncSession, tests: list[Test]) -> list[Test]:
    if not tests:
        return []

    test_ids = [test.id for test in tests]
    query = (
        select(
            Test,
            func.count(Question.id).label("questions_count"),
        )
        .select_from(Test)
        .join(Question)
        .where(Test.id.in_(test_ids))
        .group_by(Test.id)
    )

    results = await session.execute(query)
    return move_row_values_to_attributes(results, ("questions_count",))


async def update_student_test_answer_score(
    session: AsyncSession, student_test_answer: StudentTestAnswer, points: int
) -> StudentTestAnswer:
    student_test_answer.score = points
    await session.commit()
    return student_test_answer
