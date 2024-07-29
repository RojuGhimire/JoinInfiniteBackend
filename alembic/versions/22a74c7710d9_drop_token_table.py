"""Drop token table

Revision ID: 22a74c7710d9
Revises: b0566508d90f
Create Date: 2023-12-25 09:57:13.452616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22a74c7710d9'
down_revision: Union[str, None] = 'b0566508d90f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('token', sa.Column('refresh_token', sa.String(length=450), nullable=False))
    op.add_column('token', sa.Column('refresh_token_expiry', sa.DateTime(), nullable=False))
    op.alter_column('token', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_token_id'), 'token', ['id'], unique=False)
    op.create_index(op.f('ix_token_user_id'), 'token', ['user_id'], unique=True)
    op.create_foreign_key(None, 'token', 'users', ['user_id'], ['id'])
    op.drop_column('token', 'access_toke')
    op.drop_column('token', 'refresh_toke')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('refresh_toke', sa.VARCHAR(length=450), autoincrement=False, nullable=False))
    op.add_column('token', sa.Column('access_toke', sa.VARCHAR(length=450), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'token', type_='foreignkey')
    op.drop_index(op.f('ix_token_user_id'), table_name='token')
    op.drop_index(op.f('ix_token_id'), table_name='token')
    op.alter_column('token', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('token', 'refresh_token_expiry')
    op.drop_column('token', 'refresh_token')
    op.drop_column('token', 'id')
    # ### end Alembic commands ###
