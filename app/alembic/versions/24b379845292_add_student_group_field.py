"""add_student_group_field

Revision ID: 24b379845292
Revises: 781f8f7f5f67
Create Date: 2025-06-04 16:18:29.239704

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "24b379845292"
down_revision: Union[str, None] = "781f8f7f5f67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("student_test_answers", sa.Column("student_group", sa.String(), nullable=True))

    op.execute("UPDATE student_test_answers SET student_group = 'None' WHERE student_group IS NULL")

    op.alter_column("student_test_answers", "student_group", nullable=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("student_test_answers", "student_group")
    # ### end Alembic commands ###
