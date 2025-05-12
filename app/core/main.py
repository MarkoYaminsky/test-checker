from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.student_tests.handlers import student_tests_router
from app.users.handlers import users_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/users")
app.include_router(student_tests_router, prefix="/tests")
