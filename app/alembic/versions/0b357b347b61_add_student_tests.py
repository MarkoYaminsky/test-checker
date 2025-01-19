"""Add student tests

Revision ID: 0b357b347b61
Revises: da1ca37e1f14
Create Date: 2025-01-19 19:20:52.663327

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b357b347b61"
down_revision: Union[str, None] = "da1ca37e1f14"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "tests",
        sa.Column("teacher_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tests_created_at"), "tests", ["created_at"], unique=False)
    op.create_index(op.f("ix_tests_id"), "tests", ["id"], unique=False)
    op.create_table(
        "student_test_answers",
        sa.Column("test_id", sa.UUID(), nullable=False),
        sa.Column("student_username", sa.String(), nullable=False),
        sa.Column("results_photo_url", sa.String(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_id"],
            ["tests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_student_test_answers_created_at"), "student_test_answers", ["created_at"], unique=False)
    op.create_index(op.f("ix_student_test_answers_id"), "student_test_answers", ["id"], unique=False)
    op.create_table(
        "test_questions",
        sa.Column("test_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("position_number", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_id"],
            ["tests.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("test_id", "position_number", name="uix_test_questions_test_id_number"),
    )
    op.create_index(op.f("ix_test_questions_created_at"), "test_questions", ["created_at"], unique=False)
    op.create_index(op.f("ix_test_questions_id"), "test_questions", ["id"], unique=False)
    op.create_table(
        "test_answers",
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.String(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("position_number", sa.Integer(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["test_questions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "position_number", name="uix_test_answers_question_id_number"),
    )
    op.create_index(op.f("ix_test_answers_created_at"), "test_answers", ["created_at"], unique=False)
    op.create_index(op.f("ix_test_answers_id"), "test_answers", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_test_answers_id"), table_name="test_answers")
    op.drop_index(op.f("ix_test_answers_created_at"), table_name="test_answers")
    op.drop_table("test_answers")
    op.drop_index(op.f("ix_test_questions_id"), table_name="test_questions")
    op.drop_index(op.f("ix_test_questions_created_at"), table_name="test_questions")
    op.drop_table("test_questions")
    op.drop_index(op.f("ix_student_test_answers_id"), table_name="student_test_answers")
    op.drop_index(op.f("ix_student_test_answers_created_at"), table_name="student_test_answers")
    op.drop_table("student_test_answers")
    op.drop_index(op.f("ix_tests_id"), table_name="tests")
    op.drop_index(op.f("ix_tests_created_at"), table_name="tests")
    op.drop_table("tests")
    # ### end Alembic commands ###
