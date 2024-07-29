"""Changes in user and event table

Revision ID: a909a5c24a2e
Revises: 0bef7250b316
Create Date: 2023-12-26 09:37:33.059977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a909a5c24a2e'
down_revision: Union[str, None] = '0bef7250b316'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('photo_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('photo_url', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'photo_url')
    op.drop_column('event', 'photo_url')
    # ### end Alembic commands ###
