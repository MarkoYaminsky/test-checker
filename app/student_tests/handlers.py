from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.dependencies import get_db_session, get_http_authenticated_user
from app.common.handlers import check_if_object_belongs_to_user, get_object_or_404
from app.common.utilities import get_user_model
from app.student_tests.models import Answer, Question, Test
from app.student_tests.schemas import (
    AnswerCreateSchema,
    AnswerOutputSchema,
    QuestionCreateSchema,
    QuestionOutputSchema,
    StudentTestAnswerCreateSchema,
    StudentTestAnswerOutputSchema,
    TestCreateSchema,
    TestOutputSchema,
)
from app.student_tests.services import (
    create_answer,
    create_question,
    create_student_answer,
    create_test,
    delete_answer,
    delete_question,
    delete_test,
    update_answer,
    update_question,
    update_test,
)

User = get_user_model()

student_tests_router = APIRouter()


@student_tests_router.post("/", response_model=TestOutputSchema)
async def create_test_route(
    test_data: TestCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: Session = Depends(get_db_session),
):
    return create_test(session=session, teacher=user, name=test_data.name, questions=test_data.questions)


@student_tests_router.post("/{test_id}/questions/", response_model=QuestionOutputSchema)
async def create_question_route(
    test_id: str,
    question_data: QuestionCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: Session = Depends(get_db_session),
):
    test = get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    return create_question(
        session=session,
        test=test,
        content=question_data.content,
        question_type=question_data.type,
        answers=question_data.answers,
    )


@student_tests_router.post("/questions/{question_id}/answers/", response_model=AnswerOutputSchema)
async def create_answer_route(
    question_id: str,
    answer_data: AnswerCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: Session = Depends(get_db_session),
):
    question = get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(question.test.teacher, user)

    return create_answer(
        session=session, question=question, content=answer_data.content, is_correct=answer_data.is_correct
    )


@student_tests_router.get("/", response_model=list[TestOutputSchema])
async def get_tests_route(user: User = Depends(get_http_authenticated_user), _: Session = Depends(get_db_session)):
    return user.tests


@student_tests_router.get("/{test_id}/", response_model=TestOutputSchema)
async def get_test_route(test_id: str, session: Session = Depends(get_db_session)):
    test = get_object_or_404(session, Test, id=test_id)

    return test


@student_tests_router.put("/{test_id}/", response_model=TestOutputSchema)
async def update_test_route(
    test_id: str,
    test_data: TestCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: Session = Depends(get_db_session),
):
    test = get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    update_test(session=session, test=test, name=test_data.name)

    return test


@student_tests_router.put("/questions/{question_id}/", response_model=QuestionOutputSchema)
async def update_question_route(
    question_id: str,
    question_data: QuestionCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: Session = Depends(get_db_session),
):
    question = get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(question.test.teacher, user)

    return update_question(
        session=session,
        question=question,
        content=question_data.content,
    )


@student_tests_router.put("/questions/answers/{answer_id}/", response_model=AnswerOutputSchema)
async def update_answer_route(
    answer_id: str,
    answer_data: AnswerCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: Session = Depends(get_db_session),
):
    answer = get_object_or_404(session, Answer, id=answer_id)
    check_if_object_belongs_to_user(answer.question.test.teacher, user)

    return update_answer(session=session, answer=answer, content=answer_data.content, is_correct=answer_data.is_correct)


@student_tests_router.delete("/{test_id}/")
async def delete_test_route(
    test_id: str, user: User = Depends(get_http_authenticated_user), session: Session = Depends(get_db_session)
):
    test = get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    delete_test(session=session, test=test)


@student_tests_router.delete("/questions/{question_id}/")
async def delete_question_route(
    question_id: str, user: User = Depends(get_http_authenticated_user), session: Session = Depends(get_db_session)
):
    question = get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(question.test.teacher, user)

    delete_question(session=session, question=question)


@student_tests_router.delete("/questions/answers/{answer_id}/")
async def delete_answer_route(
    answer_id: str, user: User = Depends(get_http_authenticated_user), session: Session = Depends(get_db_session)
):
    answer = get_object_or_404(session, Answer, id=answer_id)
    check_if_object_belongs_to_user(answer.question.test.teacher, user)

    delete_answer(session=session, answer=answer)


@student_tests_router.post("{test_id}/submit/")
async def submit_test_answer_route(
    test_id: str, answer_data: StudentTestAnswerCreateSchema, session: Session = Depends(get_db_session)
):
    test = get_object_or_404(session, Test, id=test_id)
    return create_student_answer(
        session=session,
        test=test,
        student_username=answer_data.student_username,
        results_photo=...,  # TODO Implement this
    )


@student_tests_router.get("/{test_id}/student-answers/", response_model=list[StudentTestAnswerOutputSchema])
async def get_student_test_answers_route(
    test_id: str, user: User = Depends(get_http_authenticated_user), session: Session = Depends(get_db_session)
):
    test = get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    return test.student_test_answers  # TODO Annotate with max score and test name
