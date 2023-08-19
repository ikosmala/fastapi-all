"""add content column to posts

Revision ID: 5c9d3bbf098a
Revises: 62c130510afd
Create Date: 2023-08-19 10:57:28.116513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5c9d3bbf098a"
down_revision: Union[str, None] = "62c130510afd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "content")
