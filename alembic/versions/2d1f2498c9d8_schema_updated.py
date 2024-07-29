"""schema updated

Revision ID: 2d1f2498c9d8
Revises: d7ca66fe0b64
Create Date: 2023-12-25 09:50:33.249514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d1f2498c9d8'
down_revision: Union[str, None] = 'd7ca66fe0b64'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('token', sa.Column('refresh_token', sa.String(length=450), nullable=False))
    op.add_column('token', sa.Column('refresh_token_expiry', sa.DateTime(), nullable=False))
    op.create_index(op.f('ix_token_id'), 'token', ['id'], unique=False)
    op.create_index(op.f('ix_token_user_id'), 'token', ['user_id'], unique=True)
    op.create_foreign_key(None, 'token', 'users', ['user_id'], ['id'])
    op.drop_column('token', 'refresh_toke')
    op.drop_column('token', 'access_toke')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('access_toke', sa.VARCHAR(length=450), autoincrement=False, nullable=False))
    op.add_column('token', sa.Column('refresh_toke', sa.VARCHAR(length=450), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'token', type_='foreignkey')
    op.drop_index(op.f('ix_token_user_id'), table_name='token')
    op.drop_index(op.f('ix_token_id'), table_name='token')
    op.drop_column('token', 'refresh_token_expiry')
    op.drop_column('token', 'refresh_token')
    op.drop_column('token', 'id')
    # ### end Alembic commands ###
