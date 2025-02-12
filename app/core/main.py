from fastapi import FastAPI

from app.student_tests.handlers import student_tests_router
from app.users.handlers import users_router

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(student_tests_router, prefix="/tests")
