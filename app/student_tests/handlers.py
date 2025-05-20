from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import StreamingResponse

from app.common.decorators import expects_exceptions
from app.common.dependencies import get_db_session, get_http_authenticated_user
from app.common.handlers import check_if_object_belongs_to_user, get_object_or_404
from app.common.services.db import query_relationship
from app.common.storage import upload_test_result
from app.common.utilities import get_user_model
from app.student_tests.exceptions import DuplicateTestNameException
from app.student_tests.models import Answer, Question, Test
from app.student_tests.schemas import (
    AnswerCreateSchema,
    AnswerOutputSchema,
    AnswerUpdateSchema,
    QuestionCreateSchema,
    QuestionOutputSchema,
    QuestionUpdateSchema,
    StudentTestAnswerOutputSchema,
    TestCreateSchema,
    TestOutputSchema,
    TestUpdateSchema,
)
from app.student_tests.services import (
    create_answer,
    create_question,
    create_student_answer,
    create_test,
    delete_answer,
    delete_question,
    delete_test,
    generate_test_answers_grid,
    get_student_answers_with_test_info,
    update_answer,
    update_question,
    update_test,
)

User = get_user_model()

student_tests_router = APIRouter()


@student_tests_router.post("/", response_model=TestOutputSchema)
@expects_exceptions({DuplicateTestNameException: status.HTTP_400_BAD_REQUEST})
async def create_test_route(
    test_data: TestCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    return await create_test(session=session, teacher=user, name=test_data.name, questions=test_data.questions)


@student_tests_router.post("/{test_id}/questions/", response_model=QuestionOutputSchema)
async def create_question_route(
    test_id: UUID,
    question_data: QuestionCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    test = await get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    return await create_question(
        session=session,
        test=test,
        points=question_data.points,
        content=question_data.content,
        answers=question_data.answers,
    )


@student_tests_router.get("/{test_id}/questions/", response_model=list[QuestionOutputSchema])
async def get_questions_route(
    test_id: UUID,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    test = await get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    return await query_relationship(session, test, [Test.questions])


@student_tests_router.post("/questions/{question_id}/answers/", response_model=AnswerOutputSchema)
async def create_answer_route(
    question_id: UUID,
    answer_data: AnswerCreateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    question = await get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(
        await query_relationship(
            session=session, instance=question, relationship_attributes=[Question.test, Test.teacher]
        ),
        user,
    )

    return await create_answer(
        session=session, question=question, content=answer_data.content, is_correct=answer_data.is_correct
    )


@student_tests_router.get("/questions/{question_id}/answers/", response_model=list[AnswerOutputSchema])
async def get_answers_route(
    question_id: UUID,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    question = await get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(
        await query_relationship(
            session=session, instance=question, relationship_attributes=[Question.test, Test.teacher]
        ),
        user,
    )

    return await query_relationship(session, question, [Question.answers])


@student_tests_router.get("/", response_model=list[TestOutputSchema])
async def get_tests_route(
    user: User = Depends(get_http_authenticated_user), session: AsyncSession = Depends(get_db_session)
):
    return await query_relationship(session=session, instance=user, relationship_attributes=[User.tests])


@student_tests_router.get("/{test_id}/", response_model=TestOutputSchema)
async def get_test_route(test_id: UUID, session: AsyncSession = Depends(get_db_session)):
    return await get_object_or_404(session, Test, id=test_id)


@student_tests_router.put("/{test_id}/", response_model=TestOutputSchema)
async def update_test_route(
    test_id: UUID,
    test_data: TestUpdateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    test = await get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    await update_test(session=session, test=test, name=test_data.name, question_ids=test_data.question_ids)

    return test


@student_tests_router.put("/questions/{question_id}/", response_model=QuestionOutputSchema)
async def update_question_route(
    question_id: UUID,
    question_data: QuestionUpdateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    question = await get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(
        await query_relationship(
            session=session, instance=question, relationship_attributes=[Question.test, Test.teacher]
        ),
        user,
    )

    return await update_question(
        session=session,
        question=question,
        content=question_data.content,
    )


@student_tests_router.put("/questions/answers/{answer_id}/", response_model=AnswerOutputSchema)
async def update_answer_route(
    answer_id: UUID,
    answer_data: AnswerUpdateSchema,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    answer = await get_object_or_404(session, Answer, id=answer_id)
    check_if_object_belongs_to_user(
        await query_relationship(
            session=session, instance=answer, relationship_attributes=[Answer.question, Question.test, Test.teacher]
        ),
        user,
    )

    return await update_answer(
        session=session, answer=answer, content=answer_data.content, is_correct=answer_data.is_correct
    )


@student_tests_router.delete("/{test_id}/")
async def delete_test_route(
    test_id: UUID, user: User = Depends(get_http_authenticated_user), session: AsyncSession = Depends(get_db_session)
):
    test = await get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    await delete_test(session=session, test=test)


@student_tests_router.delete("/questions/{question_id}/")
async def delete_question_route(
    question_id: UUID,
    user: User = Depends(get_http_authenticated_user),
    session: AsyncSession = Depends(get_db_session),
):
    question = await get_object_or_404(session, Question, id=question_id)
    check_if_object_belongs_to_user(
        await query_relationship(
            session=session, instance=question, relationship_attributes=[Question.test, Test.teacher]
        ),
        user,
    )

    await delete_question(session=session, question=question)


@student_tests_router.delete("/questions/answers/{answer_id}/")
async def delete_answer_route(
    answer_id: UUID, user: User = Depends(get_http_authenticated_user), session: AsyncSession = Depends(get_db_session)
):
    answer = await get_object_or_404(session, Answer, id=answer_id)
    check_if_object_belongs_to_user(
        await query_relationship(
            session=session, instance=answer, relationship_attributes=[Answer.question, Question.test, Test.teacher]
        ),
        user,
    )

    await delete_answer(session=session, answer=answer)


@student_tests_router.post("/{test_id}/submit/")
async def submit_test_answer_route(
    test_id: UUID,
    student_username: str = Form(...),
    results_photo: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
):
    test = await get_object_or_404(session, Test, id=test_id)
    return await create_student_answer(
        session=session,
        test=test,
        student_username=student_username,
        results_url=await upload_test_result(results_photo),
    )


@student_tests_router.get("/{test_id}/student-answers/", response_model=list[StudentTestAnswerOutputSchema])
async def get_student_test_answers_route(
    test_id: UUID, user: User = Depends(get_http_authenticated_user), session: AsyncSession = Depends(get_db_session)
):
    test = await get_object_or_404(session, Test, id=test_id)
    check_if_object_belongs_to_user(test.teacher, user)

    return await get_student_answers_with_test_info(session=session, test=test)


@student_tests_router.get("/{test_id}/grid/")
async def get_test_grid(test_id: UUID, session: AsyncSession = Depends(get_db_session)):
    test = await get_object_or_404(session, Test, id=test_id)
    grid_pdf = await generate_test_answers_grid(session, test)
    return StreamingResponse(grid_pdf, media_type="application/pdf")
