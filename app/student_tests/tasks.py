from asyncio import get_event_loop

from app.common.services.db import quick_select
from app.common.services.openai import get_student_answer_grid
from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.student_tests.models import StudentTestAnswer, Test


@celery_app.task()
def grade_test(test_id: str, answer_id: str) -> None:
    from app.student_tests.services import calculate_score_by_answers_grid

    loop = get_event_loop()
    session = SessionLocal()
    test = loop.run_until_complete(quick_select(session, Test, filter_by={"id": test_id})).scalar()
    answer: StudentTestAnswer = loop.run_until_complete(
        quick_select(session, StudentTestAnswer, filter_by={"id": answer_id})
    ).scalar()
    answers_grid = get_student_answer_grid(answer)
    score = loop.run_until_complete(calculate_score_by_answers_grid(session=session, test=test, grid=answers_grid))
    answer.score = score
    loop.run_until_complete(session.commit())
