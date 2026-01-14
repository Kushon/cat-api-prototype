from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1496227b098a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('cat')


def downgrade() -> None:
    op.create_table('cat',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('weight', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('breed', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('cat_pkey'))
    )
    # ### end Alembic commands ###
